# 💸 ExpensePulse — Personal Expense Tracker & Budget Analyzer

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Community%20%7C%20Atlas-47A248.svg?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![PyMongo](https://img.shields.io/badge/PyMongo-4.8%2B-green.svg)](https://pymongo.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, full-stack personal finance web application built with **Python**, **Streamlit**, and **MongoDB (PyMongo)**. Features secure user authentication with password encryption, isolated multi-user accounts, real-time MongoDB aggregation analytics, and interactive category budget tracking with visual indicators.

---

## ✨ Features

- **🔐 Secure User Authentication & Isolation**:
  - Registration and Login with PBKDF2 (SHA-256) password hashing and unique per-user cryptographic salts.
  - Complete multi-tenant privacy: User A cannot see, edit, or aggregate User B's financial data.
- **📝 Expense CRUD Operations**:
  - Add, search, filter, update, and delete expenses with real-time input validation.
  - Multi-category tagging (Food, Travel, Shopping, Bills, etc.) and payment method classification (UPI, Cash, Cards, Net Banking).
- **🎯 Monthly Category Budgets**:
  - Set spending caps per category for any month (`YYYY-MM`).
  - Visual status cards with color-coded progress bars (Safe 🟢, Warning 🟡, Over Budget 🔴).
  - Compound unique MongoDB index on `(username, month, category)` preventing budget collisions.
- **📈 Advanced Aggregation Analytics**:
  - Real-time calculations using MongoDB `$match`, `$group`, and `$sort` aggregation pipelines.
  - Interactive category breakdown charts and daily spending trend curves powered by Altair.
- **🌐 Website-Grade UI**:
  - Sleek dark theme with responsive glassmorphism containers, live MongoDB status badge, and custom KPI summary cards.

---

## 📁 Project Structure

```plaintext
personal_expense_tracker_cli_mongodb/
├── .streamlit/
│   └── config.toml        # Streamlit theme and UI configurations
├── .env.example           # Example environment variables template
├── .gitignore             # Git exclusions for venv, cache, and secrets
├── app.py                 # Streamlit web application & authentication UI
├── database.py            # MongoDB connection, schema indexes, CRUD, and aggregations
├── requirements.txt       # Python package dependencies
└── README.md              # Complete project documentation & setup guide
```

---

## 🚀 Local Setup & Installation

### 1. Prerequisites
- **Python 3.10+** installed
- **MongoDB** Community Server running locally on port 27017, OR a **MongoDB Atlas** cloud URI.

### 2. Clone and Setup Environment

```powershell
# Clone the repository (or navigate to project directory)
git clone https://github.com/<your-username>/personal_expense_tracker_cli_mongodb.git
cd personal_expense_tracker_cli_mongodb

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1    # On Windows PowerShell
# source venv/bin/activate     # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch the Application

```powershell
streamlit run app.py
```

The app will open automatically in your browser at:
`http://localhost:8501`

---

## 🌐 Deploying to GitHub & Streamlit Cloud (Free)

### Step 1: Initialize Git and Push to GitHub

```powershell
# Initialize git repository
git init

# Add all files (venv and temp files are automatically ignored by .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: ExpensePulse with MongoDB auth and multi-user tracking"

# Create a new repository on GitHub, then link and push:
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Community Cloud (Optional)
1. Go to [share.streamlit.io](https://share.streamlit.io/) and connect your GitHub account.
2. Select your repository, branch (`main`), and main file path (`app.py`).
3. Under **Advanced Settings > Secrets**, paste your MongoDB Atlas connection string:
   ```toml
   MONGO_URI = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"
   ```
4. Click **Deploy**. Your app is now live with a public URL!

---

## 🗄️ Database Design

**Database Name**: `expense_tracker_db`

### Collections:
1. **`users`**:
   - `username`: String (Unique, Indexed)
   - `password_hash`: String (PBKDF2-SHA256)
   - `salt`: String (Cryptographic 16-byte hex)
   - `full_name`: String
   - `email`: String
   - `created_at`: Date
   - `last_login`: Date

2. **`expenses`**:
   - `title`: String
   - `amount`: Double
   - `category`: String
   - `expense_date`: ISODate
   - `payment_method`: String
   - `notes`: String
   - `username`: String (Indexed with `expense_date`)
   - `created_at`: Date
   - `updated_at`: Date

3. **`budgets`**:
   - `username`: String
   - `month`: String (`YYYY-MM`)
   - `category`: String
   - `limit`: Double
   - `created_at`: Date
   - `updated_at`: Date
   - *Index*: Unique compound index on `(username, month, category)`

---

## 💻 CLI Verification with `mongosh`

Open a terminal to interact directly with the database:

```powershell
mongosh
```

```javascript
// Connect to database
use expense_tracker_db

// View collections
show collections

// Inspect registered users
db.users.find({}, { password_hash: 0, salt: 0 }).pretty()

// View expenses for a specific user
db.expenses.find({ username: "demo" }).pretty()

// Run aggregation to calculate monthly spending by category
db.expenses.aggregate([
  { $match: { username: "demo" } },
  { $group: { _id: "$category", totalSpent: { $sum: "$amount" }, count: { $sum: 1 } } },
  { $sort: { totalSpent: -1 } }
])
```

---

## 📋 Viva & Academic Checklist

- [x] **MongoDB Integration**: Yes, connected via PyMongo with automatic index creation.
- [x] **User Authentication & Security**: Yes, PBKDF2 hashing with salt stored in `users` collection.
- [x] **Multi-User Data Isolation**: Yes, strict per-user queries for expenses, budgets, and aggregations.
- [x] **CRUD Implementation**: Complete Create, Read, Update, Delete for expenses and budgets.
- [x] **Aggregation Pipelines**: Real-time spending summary, category totals, and daily trends using `$match`, `$group`, and `$sort`.
- [x] **Modular Architecture**: Clean separation between UI (`app.py`) and backend database logic (`database.py`).
- [x] **CLI Demonstration**: Verifiable using `mongosh`.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
