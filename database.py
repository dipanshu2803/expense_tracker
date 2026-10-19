import os
import hashlib
import secrets
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "expense_tracker_db"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)
    client.admin.command("ping")
    db = client[DATABASE_NAME]
    expenses = db["expenses"]
    budgets = db["budgets"]
    users = db["users"]

    # Compound indexes for strict per-user data isolation:
    expenses.create_index([("username", ASCENDING), ("expense_date", DESCENDING)])
    expenses.create_index([("username", ASCENDING), ("category", ASCENDING)])
    budgets.create_index([("username", ASCENDING), ("month", ASCENDING), ("category", ASCENDING)], unique=True)
    users.create_index([("username", ASCENDING)], unique=True)
except Exception as e:
    client = None
    db = None
    expenses = None
    budgets = None
    users = None


# --- Authentication & User Management ---

def hash_password(password, salt=None):
    """Hash a password using PBKDF2 with SHA-256 and a random salt."""
    if not salt:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return pwd_hash, salt


def verify_password(password, pwd_hash, salt):
    """Verify if a candidate password matches the stored hash with salt."""
    check_hash, _ = hash_password(password, salt)
    return check_hash == pwd_hash


def register_user(username, password, full_name="", email=""):
    """Register a new user in MongoDB users collection with hashed credentials."""
    username = username.strip().lower()
    if not username or len(username) < 3:
        raise ValueError("Username must be at least 3 characters long.")
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    if users.find_one({"username": username}):
        raise ValueError(f"Username '{username}' is already taken. Please choose another.")

    pwd_hash, salt = hash_password(password)
    user_doc = {
        "username": username,
        "password_hash": pwd_hash,
        "salt": salt,
        "full_name": full_name.strip() or username.capitalize(),
        "email": email.strip().lower(),
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow()
    }
    result = users.insert_one(user_doc)
    return result.inserted_id


def authenticate_user(username, password):
    """Authenticate user credentials and update last login timestamp."""
    username = username.strip().lower()
    user = users.find_one({"username": username})
    if not user:
        return None

    if verify_password(password, user["password_hash"], user["salt"]):
        users.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.utcnow()}})
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "full_name": user.get("full_name", user["username"]),
            "email": user.get("email", ""),
            "created_at": user.get("created_at")
        }
    return None


def get_user_by_username(username):
    """Retrieve user profile by username."""
    user = users.find_one({"username": username.strip().lower()})
    if user:
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "full_name": user.get("full_name", user["username"]),
            "email": user.get("email", ""),
            "created_at": user.get("created_at")
        }
    return None


# --- Per-User Expense Management ---

def add_expense(title, amount, category, expense_date, payment_method, username, notes=""):
    """Create one expense for a specific user after validating its values."""
    if not username or not username.strip():
        raise ValueError("A valid username is required to track expenses per user.")

    errors = validate_expense(title, amount, category, expense_date, payment_method)
    if errors:
        raise ValueError("; ".join(errors))

    doc = {
        "title": title.strip(),
        "amount": round(float(amount), 2),
        "category": category,
        "expense_date": expense_date,
        "payment_method": payment_method,
        "notes": notes.strip(),
        "username": username.strip().lower(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    return expenses.insert_one(doc).inserted_id


def validate_expense(title, amount, category, expense_date, payment_method):
    errors = []
    allowed_categories = ["Food", "Travel", "Shopping", "Education", "Bills", "Health", "Entertainment", "Other"]
    allowed_methods = ["Cash", "UPI", "Debit Card", "Credit Card", "Net Banking", "Other"]

    if not isinstance(title, str) or len(title.strip()) < 2:
        errors.append("Description must contain at least 2 characters.")
    try:
        amount = float(amount)
        if amount <= 0 or amount > 10_000_000:
            errors.append("Amount must be greater than 0 and no more than 10000000.")
    except (TypeError, ValueError):
        errors.append("Amount must be a valid number.")
    if category not in allowed_categories:
        errors.append("Invalid category.")
    if not isinstance(expense_date, datetime):
        errors.append("Expense date must be a datetime value.")
    elif expense_date.date() > datetime.now().date():
        errors.append("Expense date cannot be in the future.")
    if payment_method not in allowed_methods:
        errors.append("Invalid payment method.")
    return errors


def list_expenses(username, category=None, title_search=None):
    """Read expense records strictly belonging to the given user."""
    if not username:
        return []
    query = {"username": username.strip().lower()}
    if category and category != "All":
        query["category"] = category
    if title_search:
        query["title"] = {"$regex": title_search, "$options": "i"}
    return list(expenses.find(query).sort("expense_date", DESCENDING))


def update_expense(expense_id, username, title, amount, category, expense_date, payment_method, notes=""):
    """Update an existing expense strictly owned by the given user."""
    from bson import ObjectId
    errors = validate_expense(title, amount, category, expense_date, payment_method)
    if errors:
        raise ValueError("; ".join(errors))
    result = expenses.update_one(
        {"_id": ObjectId(expense_id), "username": username.strip().lower()},
        {"$set": {
            "title": title.strip(),
            "amount": round(float(amount), 2),
            "category": category,
            "expense_date": expense_date,
            "payment_method": payment_method,
            "notes": notes.strip(),
            "updated_at": datetime.utcnow()
        }}
    )
    return result.modified_count


def delete_expense(expense_id, username):
    """Delete one expense strictly owned by the given user."""
    from bson import ObjectId
    result = expenses.delete_one({"_id": ObjectId(expense_id), "username": username.strip().lower()})
    return result.deleted_count


# --- Per-User Budget Management ---

def set_budget(username, month, category, limit_amount):
    """Create or update a monthly category budget for a specific user."""
    if not username:
        raise ValueError("A valid username is required to set a user budget.")
    allowed_categories = ["Food", "Travel", "Shopping", "Education", "Bills", "Health", "Entertainment", "Other"]
    if category not in allowed_categories:
        raise ValueError("Invalid category.")
    if float(limit_amount) <= 0:
        raise ValueError("Budget limit must be greater than zero.")
    if len(month) != 7 or month[4] != "-" or not month[:4].isdigit() or not month[5:].isdigit() or not 1 <= int(month[5:]) <= 12:
        raise ValueError("Month must use YYYY-MM format, e.g. 2026-10.")

    b_filter = {"username": username.strip().lower(), "month": month, "category": category}
    update_doc = {
        "$set": {"limit": round(float(limit_amount), 2), "updated_at": datetime.utcnow()},
        "$setOnInsert": {"created_at": datetime.utcnow(), "username": username.strip().lower()}
    }
    budgets.update_one(b_filter, update_doc, upsert=True)


# --- Per-User Aggregation Analytics ---

def category_aggregation(username, month):
    """MongoDB aggregation: category totals and transaction counts for a specific user in YYYY-MM."""
    start = datetime.strptime(month + "-01", "%Y-%m-%d")
    if start.month == 12:
        end = datetime(start.year + 1, 1, 1)
    else:
        end = datetime(start.year, start.month + 1, 1)

    match_stage = {
        "username": username.strip().lower(),
        "expense_date": {"$gte": start, "$lt": end}
    }

    pipeline = [
        {"$match": match_stage},
        {"$group": {
            "_id": "$category",
            "total_spent": {"$sum": "$amount"},
            "transaction_count": {"$sum": 1},
            "average_expense": {"$avg": "$amount"}
        }},
        {"$sort": {"total_spent": -1}}
    ]
    return list(expenses.aggregate(pipeline))


def monthly_summary(username, month):
    """MongoDB aggregation: user monthly total, count, and average expense."""
    start = datetime.strptime(month + "-01", "%Y-%m-%d")
    end = datetime(start.year + 1, 1, 1) if start.month == 12 else datetime(start.year, start.month + 1, 1)

    match_stage = {
        "username": username.strip().lower(),
        "expense_date": {"$gte": start, "$lt": end}
    }

    pipeline = [
        {"$match": match_stage},
        {"$group": {
            "_id": None,
            "total_spent": {"$sum": "$amount"},
            "transaction_count": {"$sum": 1},
            "average_expense": {"$avg": "$amount"}
        }}
    ]
    result = list(expenses.aggregate(pipeline))
    return result[0] if result else {"total_spent": 0, "transaction_count": 0, "average_expense": 0}


def budget_status(username, month):
    """Compare each saved budget for a user with their category spending in the chosen month."""
    category_totals = {item["_id"]: item["total_spent"] for item in category_aggregation(username, month)}
    b_filter = {"username": username.strip().lower(), "month": month}

    results = []
    for budget in budgets.find(b_filter).sort("category", ASCENDING):
        spent = category_totals.get(budget["category"], 0)
        results.append({
            "category": budget["category"],
            "budget": budget["limit"],
            "spent": round(spent, 2),
            "remaining": round(budget["limit"] - spent, 2),
            "status": "Over budget" if spent > budget["limit"] else "Within budget"
        })
    return results
