import os
import hashlib
import secrets
from datetime import date, datetime
from calendar import month_name

import pandas as pd
import streamlit as st
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from bson.objectid import ObjectId
import altair as alt

# --- Page Configuration ---
st.set_page_config(
    page_title="ExpensePulse • Personal Expense Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Modern Website Styling (CSS) ---
st.markdown(
    """<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"], .stMarkdown, p, div, span {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Overall background styling with subtle radial mesh */
    .stApp {
        background: radial-gradient(ellipse at 50% -10%, rgba(16, 185, 129, 0.08), rgba(11, 15, 25, 0) 60%),
                    linear-gradient(180deg, #0B0F19 0%, #070A12 100%);
    }

    /* Hide standard Streamlit header elements */
    button[data-testid='stMainMenuItem-theme-System'],
    div[data-testid='stStatusWidget'],
    div[data-testid='stMainMenuList'] + div,
    header[data-testid='stHeader'] {
        background: transparent !important;
    }

    /* Custom App Hero / Topbar */
    .hero-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 24px;
        background: rgba(17, 24, 39, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }

    .hero-brand {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .hero-icon-box {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: linear-gradient(135deg, #10B981 0%, #047857 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: 0 6px 18px rgba(16, 185, 129, 0.35);
    }

    .hero-title {
        font-size: 1.45rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #F9FAFB;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .hero-badge {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 3px 9px;
        border-radius: 20px;
    }

    .hero-subtitle {
        font-size: 0.85rem;
        color: #9CA3AF;
        margin-top: 2px;
    }

    .hero-right-actions {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .hero-status-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.8rem;
        color: #34D399;
        font-weight: 600;
    }

    .user-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.82rem;
        color: #A5B4FC;
        font-weight: 600;
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse 1.8s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Auth Box / Container */
    .auth-wrapper {
        max-width: 480px;
        margin: 40px auto;
        background: rgba(17, 24, 39, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 36px 32px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(16, 185, 129, 0.1);
    }

    .auth-header {
        text-align: center;
        margin-bottom: 24px;
    }

    .auth-logo {
        width: 60px;
        height: 60px;
        border-radius: 16px;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        margin-bottom: 14px;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
    }

    .auth-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #F9FAFB;
        letter-spacing: -0.02em;
    }

    .auth-subtitle {
        font-size: 0.86rem;
        color: #9CA3AF;
        margin-top: 6px;
    }

    .auth-card-feature-pill {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-top: 24px;
        padding-top: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        font-size: 0.75rem;
        color: #9CA3AF;
    }

    /* Profile Card in Sidebar */
    .profile-card {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .avatar-circle {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: #FFFFFF;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
    }

    .profile-info {
        flex: 1;
        overflow: hidden;
    }

    .profile-name {
        font-weight: 700;
        font-size: 0.92rem;
        color: #F9FAFB;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }

    .profile-username {
        font-size: 0.75rem;
        color: #9CA3AF;
    }

    /* KPI Summary Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }

    .kpi-card {
        background: rgba(17, 24, 39, 0.65);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 16px 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(16, 185, 129, 0.3);
    }

    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #9CA3AF;
        margin-bottom: 6px;
    }

    .kpi-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.55rem;
        font-weight: 700;
        color: #F9FAFB;
        letter-spacing: -0.02em;
    }

    .kpi-sub {
        font-size: 0.75rem;
        color: #6B7280;
        margin-top: 4px;
    }

    /* Segmented Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 5px;
        gap: 4px;
        margin-bottom: 22px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 10px;
        color: #9CA3AF;
        font-weight: 500;
        font-size: 0.88rem;
        padding: 6px 16px;
        border: none !important;
        background: transparent;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #F3F4F6;
        background: rgba(255, 255, 255, 0.05);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
    }

    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Web Card Styling */
    .web-panel {
        background: rgba(17, 24, 39, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.35);
    }

    .panel-header {
        margin-bottom: 18px;
    }

    .panel-title {
        font-size: 1.18rem;
        font-weight: 700;
        color: #F9FAFB;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .panel-desc {
        font-size: 0.82rem;
        color: #9CA3AF;
        margin-top: 3px;
    }

    /* Buttons */
    button[kind="primary"] {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.4rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.2s ease !important;
    }

    button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45) !important;
    }

    /* Progress bar cards for budget */
    .budget-card {
        background: rgba(17, 24, 39, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }

    .budget-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }

    .budget-cat-name {
        font-weight: 600;
        color: #F9FAFB;
        font-size: 0.95rem;
    }

    .budget-badge-safe {
        font-size: 0.72rem;
        font-weight: 700;
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 2px 8px;
        border-radius: 12px;
    }

    .budget-badge-warn {
        font-size: 0.72rem;
        font-weight: 700;
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 2px 8px;
        border-radius: 12px;
    }

    .budget-badge-danger {
        font-size: 0.72rem;
        font-weight: 700;
        background: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 2px 8px;
        border-radius: 12px;
    }

    .budget-numbers-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        color: #9CA3AF;
        margin-bottom: 6px;
        font-family: 'JetBrains Mono', monospace;
    }

    .track {
        width: 100%;
        height: 7px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        overflow: hidden;
    }

    .fill-safe {
        height: 100%;
        background: linear-gradient(90deg, #10B981, #34D399);
        border-radius: 10px;
    }

    .fill-warn {
        height: 100%;
        background: linear-gradient(90deg, #F59E0B, #FCD34D);
        border-radius: 10px;
    }

    .fill-danger {
        height: 100%;
        background: linear-gradient(90deg, #EF4444, #F87171);
        border-radius: 10px;
    }

    /* Footer */
    .app-footer {
        margin-top: 40px;
        padding: 20px 0;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.8rem;
        color: #6B7280;
    }

    .footer-tags {
        display: flex;
        gap: 8px;
    }

    .tag-pill {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
        color: #9CA3AF;
    }
    </style>""",
    unsafe_allow_html=True,
)

# --- MongoDB Database Setup & Connection ---
DB_NAME = "expense_tracker_db"

@st.cache_resource
def connect(uri):
    client = MongoClient(uri, serverSelectionTimeoutMS=4000)
    client.admin.command("ping")
    db = client[DB_NAME]
    expenses = db["expenses"]
    budgets = db["budgets"]
    users = db["users"]
    expenses.create_index([("username", 1), ("expense_date", -1)])
    expenses.create_index([("username", 1), ("category", 1)])
    budgets.create_index([("username", 1), ("month", 1), ("category", 1)], unique=True)
    users.create_index([("username", 1)], unique=True)
    return expenses, budgets, users

# --- Authentication Helpers ---
def hash_password(password, salt=None):
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
    check_hash, _ = hash_password(password, salt)
    return check_hash == pwd_hash

def register_user(users_col, username, password, full_name="", email=""):
    username = username.strip().lower()
    if not username or len(username) < 3:
        raise ValueError("Username must be at least 3 characters long.")
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    if users_col.find_one({"username": username}):
        raise ValueError(f"Username '{username}' already exists. Please pick another.")

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
    users_col.insert_one(user_doc)
    return {
        "username": user_doc["username"],
        "full_name": user_doc["full_name"],
        "email": user_doc["email"]
    }

def authenticate_user(users_col, username, password):
    username = username.strip().lower()
    user = users_col.find_one({"username": username})
    if not user:
        return None
    if verify_password(password, user["password_hash"], user["salt"]):
        users_col.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.utcnow()}})
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "full_name": user.get("full_name", user["username"]),
            "email": user.get("email", "")
        }
    return None

# --- Session State Initialization ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

# --- Sidebar Connection Configuration ---
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
            <div style="width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, #10B981, #059669); display: flex; align-items: center; justify-content: center; font-size: 20px;">
                💸
            </div>
            <div>
                <div style="font-size: 1.1rem; font-weight: 800; color: #F9FAFB;">ExpensePulse</div>
                <div style="font-size: 0.75rem; color: #9CA3AF;">MongoDB Multi-User Engine</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("**Database Configuration**")
    MONGO_URI = st.text_input(
        "MongoDB URI",
        value=os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
        type="password",
        help="Default localhost URI or MongoDB Atlas connection string"
    )

try:
    expenses, budgets, users = connect(MONGO_URI)
except Exception as exc:
    st.sidebar.error("MongoDB connection failed")
    st.error("MongoDB connection failed. Start MongoDB locally or verify your Atlas URI in the sidebar.")
    st.code(str(exc))
    st.stop()

# --- User Profile & Logout in Sidebar (when authenticated) ---
with st.sidebar:
    st.markdown(
        """
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px; padding: 10px 14px; margin-top: 8px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 8px; color: #34D399; font-weight: 600; font-size: 0.85rem;">
                <span style="width: 7px; height: 7px; border-radius: 50%; background-color: #10B981;"></span>
                Connected to MongoDB
            </div>
            <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 4px;">
                Database: <code>expense_tracker_db</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state["authenticated"] and st.session_state["user"]:
        curr_user = st.session_state["user"]
        initials = (curr_user["full_name"][:2] if curr_user["full_name"] else curr_user["username"][:2]).upper()
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="avatar-circle">{initials}</div>
                <div class="profile-info">
                    <div class="profile-name">{curr_user['full_name']}</div>
                    <div class="profile-username">@{curr_user['username']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()

        # Display user-specific statistics
        my_exp_count = expenses.count_documents({"username": curr_user["username"]})
        my_bud_count = budgets.count_documents({"username": curr_user["username"]})
        total_users_count = users.count_documents({})

        st.markdown("**Your Account Summary**")
        col_sb1, col_sb2 = st.columns(2)
        col_sb1.metric("Your Expenses", my_exp_count)
        col_sb2.metric("Your Budgets", my_bud_count)

        st.caption(f"Registered system users: {total_users_count}")

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.76rem; color: #9CA3AF; line-height: 1.5;">
            <strong style="color: #E5E7EB;">Per-User Data Isolation:</strong><br/>
            Each registered user tracks their own separate expenses, budgets, and analytics.<br/><br/>
            <strong style="color: #E5E7EB;">CLI Verification:</strong><br/>
            <code>mongosh</code><br/>
            <code>use expense_tracker_db</code><br/>
            <code>db.expenses.find({username: "your_user"})</code>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# AUTHENTICATION SCREEN (LOGIN & SIGN UP PORTAL)
# ==============================================================================
if not st.session_state["authenticated"]:
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-brand">
                <div class="hero-icon-box">💸</div>
                <div>
                    <div class="hero-title">
                        ExpensePulse
                        <span class="hero-badge">Multi-User Portal</span>
                    </div>
                    <div class="hero-subtitle">Personal Expense Tracker & Budget Analyzer • Isolated Per-User Accounts</div>
                </div>
            </div>
            <div class="hero-status-pill">
                <span class="pulse-dot"></span>
                <span>MongoDB Live</span>
                <span style="opacity: 0.6; margin: 0 4px;">•</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;">expense_tracker_db</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    auth_col1, auth_col2, auth_col3 = st.columns([1, 1.8, 1])
    with auth_col2:
        st.markdown(
            """
            <div class="auth-header">
                <div class="auth-logo">🔐</div>
                <div class="auth-title">Welcome to ExpensePulse</div>
                <div class="auth-subtitle">Sign in to track your personal expenses or register a new isolated account</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        tab_login, tab_signup = st.tabs(["🔑 Sign In", "✨ Create Account"])

        with tab_login:
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            with st.form("login_form"):
                login_user = st.text_input("Username", placeholder="e.g. demo or your registered username")
                login_pass = st.text_input("Password", type="password", placeholder="Enter your password")
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                login_submit = st.form_submit_button("Sign In to Dashboard", type="primary", use_container_width=True)

            if login_submit:
                if not login_user.strip() or not login_pass:
                    st.error("⚠️ Please enter both username and password.")
                else:
                    user_data = authenticate_user(users, login_user, login_pass)
                    if user_data:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = user_data
                        st.success(f"🎉 Welcome back, {user_data['full_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password. Please verify and try again.")

            st.markdown(
                """
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 10px; padding: 12px 14px; margin-top: 18px; font-size: 0.8rem; color: #9CA3AF;">
                    💡 <strong>Test Account:</strong> You can log in with <code>demo</code> / <code>demopass123</code> or switch to <em>Create Account</em> to test with a completely fresh user profile.
                </div>
                """,
                unsafe_allow_html=True
            )

        with tab_signup:
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            with st.form("signup_form"):
                new_fullname = st.text_input("Full Name", placeholder="e.g. Rachel Green")
                new_username = st.text_input("Username *", placeholder="Choose a unique username (min 3 chars)")
                new_email = st.text_input("Email (Optional)", placeholder="e.g. rachel@example.com")
                new_password = st.text_input("Password *", type="password", placeholder="Minimum 6 characters")
                new_password_confirm = st.text_input("Confirm Password *", type="password", placeholder="Re-type your password")

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                signup_submit = st.form_submit_button("✨ Create Account & Sign In", type="primary", use_container_width=True)

            if signup_submit:
                if not new_username.strip():
                    st.error("⚠️ Username is required.")
                elif len(new_username.strip()) < 3:
                    st.error("⚠️ Username must be at least 3 characters long.")
                elif len(new_password) < 6:
                    st.error("⚠️ Password must be at least 6 characters long.")
                elif new_password != new_password_confirm:
                    st.error("⚠️ Passwords do not match. Please verify and re-type.")
                else:
                    try:
                        user_info = register_user(users, new_username, new_password, new_fullname, new_email)
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = user_info
                        st.success(f"🎉 Account created successfully! Welcome, {user_info['full_name']}!")
                        st.rerun()
                    except ValueError as ve:
                        st.error(f"⚠️ {ve}")
                    except PyMongoError as pe:
                        st.error(f"Database error: {pe}")

        st.markdown(
            """
            <div class="auth-card-feature-pill">
                <span>🔒 PBKDF2 Encrypted</span>
                <span>•</span>
                <span>🛡️ 100% User Isolation</span>
                <span>•</span>
                <span>🍃 MongoDB Powered</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Stop execution here if user is not authenticated
    st.stop()


# ==============================================================================
# AUTHENTICATED USER DASHBOARD (STRICT USER ISOLATION)
# ==============================================================================

logged_in_user = st.session_state["user"]
active_username = logged_in_user["username"].strip().lower()

CATEGORY_ICONS = {
    "Food": "🍔",
    "Travel": "✈️",
    "Shopping": "🛍️",
    "Education": "📚",
    "Bills": "⚡",
    "Health": "💊",
    "Entertainment": "🎬",
    "Other": "🏷️"
}

CATEGORIES = list(CATEGORY_ICONS.keys())
PAYMENT_METHODS = ["Cash", "UPI", "Debit Card", "Credit Card", "Net Banking", "Other"]

def validate_expense(title, amount, category, expense_date, payment_method):
    errors = []
    if not title.strip() or len(title.strip()) < 2:
        errors.append("Description must contain at least 2 characters.")
    if amount <= 0:
        errors.append("Amount must be greater than zero.")
    if amount > 10_000_000:
        errors.append("Amount is unusually large; enter a value below ₹1,00,00,000.")
    if category not in CATEGORIES:
        errors.append("Choose a valid category.")
    if not expense_date:
        errors.append("Expense date is required.")
    if payment_method not in PAYMENT_METHODS:
        errors.append("Choose a valid payment method.")
    return errors

def expense_doc(title, amount, category, expense_date, payment_method, notes, username):
    return {
        "title": title.strip(),
        "amount": round(float(amount), 2),
        "category": category,
        "expense_date": datetime.combine(expense_date, datetime.min.time()),
        "payment_method": payment_method,
        "notes": notes.strip(),
        "username": username,
        "updated_at": datetime.utcnow()
    }

def show_errors(errors):
    for error in errors:
        st.error(f"⚠️ {error}")

def month_key(d):
    return d.strftime("%Y-%m")

def money(value):
    return f"₹{value:,.2f}"

# --- Top Web Hero Bar with User Profile ---
st.markdown(
    f"""
    <div class="hero-container">
        <div class="hero-brand">
            <div class="hero-icon-box">💸</div>
            <div>
                <div class="hero-title">
                    ExpensePulse
                    <span class="hero-badge">Private Workspace</span>
                </div>
                <div class="hero-subtitle">Personal Expense Tracker & Budget Analyzer • User: <strong>{logged_in_user['full_name']}</strong></div>
            </div>
        </div>
        <div class="hero-right-actions">
            <div class="user-pill">
                <span>👤</span>
                <span>{logged_in_user['full_name']}</span>
                <span style="opacity: 0.5;">(@{active_username})</span>
            </div>
            <div class="hero-status-pill">
                <span class="pulse-dot"></span>
                <span>MongoDB Live</span>
                <span style="opacity: 0.6; margin: 0 4px;">•</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;">expense_tracker_db</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Real-Time KPI Stats Strip (Strictly for Active User in Current Month) ---
today = date.today()
curr_key = month_key(today)
curr_start = datetime(today.year, today.month, 1)
curr_end = datetime(today.year + 1, 1, 1) if today.month == 12 else datetime(today.year, today.month + 1, 1)

# Aggregation match strictly filtered by active_username
current_user_month_match = {
    "$match": {
        "username": active_username,
        "expense_date": {"$gte": curr_start, "$lt": curr_end}
    }
}

current_month_stats = list(expenses.aggregate([
    current_user_month_match,
    {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}, "avg": {"$avg": "$amount"}}}
]))

cm_total = current_month_stats[0]["total"] if current_month_stats else 0.0
cm_count = current_month_stats[0]["count"] if current_month_stats else 0
cm_avg = current_month_stats[0]["avg"] if current_month_stats else 0.0
curr_budgets_count = budgets.count_documents({"username": active_username, "month": curr_key})

st.markdown(
    f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Your Month Spending</div>
            <div class="kpi-val" style="color: #34D399;">{money(cm_total)}</div>
            <div class="kpi-sub">Total spent by @{active_username} in {today.strftime('%B %Y')}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Your Transactions</div>
            <div class="kpi-val">{cm_count}</div>
            <div class="kpi-sub">Records logged this month</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Your Average Expense</div>
            <div class="kpi-val">{money(cm_avg)}</div>
            <div class="kpi-sub">Per transaction in {today.strftime('%b')}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Your Active Budgets</div>
            <div class="kpi-val">{curr_budgets_count}</div>
            <div class="kpi-sub">Categories budgeted for {curr_key}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Segmented Modern Web Tabs ---
tab_add, tab_view, tab_edit, tab_delete, tab_budget, tab_reports = st.tabs([
    "➕ Add Expense",
    "📋 View / Search",
    "✏️ Update Expense",
    "🗑️ Delete Expense",
    "🎯 Monthly Budgets",
    "📈 Analytics"
])

# ==============================================================================
# TAB 1: ADD EXPENSE (SAVED TO CURRENT USER)
# ==============================================================================
with tab_add:
    st.markdown(
        f"""
        <div class="web-panel">
            <div class="panel-header">
                <div class="panel-title">📝 Record a New Expense for @{active_username}</div>
                <div class="panel-desc">Add a personal transaction to your isolated MongoDB ledger with real-time validation</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Expense Description *", placeholder="e.g. Grocery shopping, Metro card recharge")
            category = st.selectbox("Category *", CATEGORIES, format_func=lambda c: f"{CATEGORY_ICONS.get(c, '')} {c}")
            payment_method = st.selectbox("Payment Method *", PAYMENT_METHODS)
        with col2:
            amount = st.number_input("Amount (₹) *", min_value=0.0, max_value=10_000_000.0, value=100.0, step=10.0, format="%.2f")
            expense_date = st.date_input("Date of Expense *", value=date.today(), max_value=date.today())
            notes = st.text_input("Notes (Optional)", placeholder="e.g. Shared with roommates")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 Save Expense to Database", type="primary", use_container_width=True)

    if submitted:
        errors = validate_expense(title, amount, category, expense_date, payment_method)
        if errors:
            show_errors(errors)
        else:
            doc = expense_doc(title, amount, category, expense_date, payment_method, notes, active_username)
            doc["created_at"] = datetime.utcnow()
            try:
                result = expenses.insert_one(doc)
                st.success(f"✅ Expense saved successfully for @{active_username}! Record ID: `{result.inserted_id}`")
                st.rerun()
            except PyMongoError as exc:
                st.error(f"Database error: {exc}")

# ==============================================================================
# TAB 2: VIEW / SEARCH (FILTERED STRICTLY BY CURRENT USER)
# ==============================================================================
with tab_view:
    st.markdown(
        f"""
        <div class="web-panel">
            <div class="panel-header">
                <div class="panel-title">📋 Expense Records for @{active_username}</div>
                <div class="panel-desc">Search, filter, and inspect only your personal transactions in MongoDB</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    f1, f2 = st.columns([2, 1])
    search = f1.text_input("🔍 Search description", placeholder="Type keywords like 'lunch', 'rent', 'shopping'...")
    filter_category = f2.selectbox("Filter by category", ["All Categories"] + CATEGORIES,
                                   format_func=lambda c: f"All Categories" if c == "All Categories" else f"{CATEGORY_ICONS.get(c, '')} {c}")

    # Strict query for current user only
    query = {"username": active_username}
    if search.strip():
        query["title"] = {"$regex": search.strip().replace(".", r"\."), "$options": "i"}
    if filter_category != "All Categories":
        query["category"] = filter_category

    try:
        rows = list(expenses.find(query).sort("expense_date", -1))
        if rows:
            total_filtered = sum(r["amount"] for r in rows)
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding: 8px 12px; background: rgba(255,255,255,0.03); border-radius: 8px; font-size: 0.85rem; color: #9CA3AF;">
                    <span>Found <strong>{len(rows)}</strong> transaction(s) for <strong>@{active_username}</strong></span>
                    <span>Total Sum: <strong style="color: #34D399; font-family: 'JetBrains Mono', monospace;">{money(total_filtered)}</strong></span>
                </div>
                """,
                unsafe_allow_html=True
            )

            display = [{
                "Date": r["expense_date"].strftime("%Y-%m-%d"),
                "Category": f"{CATEGORY_ICONS.get(r['category'], '')} {r['category']}",
                "Description": r["title"],
                "Amount": f"₹{r['amount']:,.2f}",
                "Payment Method": r["payment_method"],
                "Notes": r.get("notes", "") or "—"
            } for r in rows]

            st.dataframe(
                pd.DataFrame(display),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.TextColumn("Date", width="small"),
                    "Category": st.column_config.TextColumn("Category", width="medium"),
                    "Description": st.column_config.TextColumn("Description", width="large"),
                    "Amount": st.column_config.TextColumn("Amount", width="medium"),
                    "Payment Method": st.column_config.TextColumn("Payment", width="medium"),
                    "Notes": st.column_config.TextColumn("Notes", width="large"),
                }
            )
        else:
            st.info(f"ℹ️ No expenses recorded for @{active_username} matching the filter. Head over to 'Add Expense' to log your transactions!")
    except PyMongoError as exc:
        st.error(f"Database error: {exc}")

# ==============================================================================
# TAB 3: UPDATE EXPENSE (ONLY CURRENT USER'S EXPENSES)
# ==============================================================================
with tab_edit:
    st.markdown(
        f"""
        <div class="web-panel">
            <div class="panel-header">
                <div class="panel-title">✏️ Update an Expense (@{active_username})</div>
                <div class="panel-desc">Modify any of your previously recorded transactions and save updates to MongoDB</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    user_expenses = list(expenses.find({"username": active_username}).sort("expense_date", -1))
    if not user_expenses:
        st.info(f"ℹ️ No expenses found under account @{active_username} to update. Add an expense first!")
    else:
        choices = {f"{r['expense_date'].strftime('%Y-%m-%d')} • {CATEGORY_ICONS.get(r['category'], '')} {r['title']} ({money(r['amount'])})": r["_id"] for r in user_expenses}
        selected = st.selectbox("Choose expense to modify", list(choices.keys()), key="edit_expense_choice")
        current = expenses.find_one({"_id": choices[selected], "username": active_username})

        if current:
            with st.form("edit_expense_form"):
                c1, c2 = st.columns(2)
                e_title = c1.text_input("Description", value=current["title"])
                e_amount = c2.number_input("Amount (₹)", min_value=0.0, max_value=10_000_000.0, value=float(current["amount"]), step=10.0, format="%.2f")
                current_cat_idx = CATEGORIES.index(current["category"]) if current["category"] in CATEGORIES else 0
                e_category = c1.selectbox("Category", CATEGORIES, index=current_cat_idx, format_func=lambda c: f"{CATEGORY_ICONS.get(c, '')} {c}")
                current_date = current["expense_date"].date() if isinstance(current["expense_date"], datetime) else current["expense_date"]
                e_date = c2.date_input("Date", value=current_date, max_value=date.today())
                current_pay_idx = PAYMENT_METHODS.index(current["payment_method"]) if current["payment_method"] in PAYMENT_METHODS else 0
                e_payment = c1.selectbox("Payment method", PAYMENT_METHODS, index=current_pay_idx)
                e_notes = c2.text_input("Notes", value=current.get("notes", ""))

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                save = st.form_submit_button("💾 Save Changes to MongoDB", type="primary", use_container_width=True)

            if save:
                errs = validate_expense(e_title, e_amount, e_category, e_date, e_payment)
                if errs:
                    show_errors(errs)
                else:
                    try:
                        expenses.update_one(
                            {"_id": current["_id"], "username": active_username},
                            {"$set": expense_doc(e_title, e_amount, e_category, e_date, e_payment, e_notes, active_username)}
                        )
                        st.success("✅ Expense updated successfully!")
                        st.rerun()
                    except PyMongoError as exc:
                        st.error(f"Database error: {exc}")

# ==============================================================================
# TAB 4: DELETE EXPENSE (ONLY CURRENT USER'S EXPENSES)
# ==============================================================================
with tab_delete:
    st.markdown(
        f"""
        <div class="web-panel">
            <div class="panel-header">
                <div class="panel-title">🗑️ Delete an Expense Record (@{active_username})</div>
                <div class="panel-desc">Permanently remove one of your transactions from MongoDB</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    user_expenses = list(expenses.find({"username": active_username}).sort("expense_date", -1))
    if not user_expenses:
        st.info(f"ℹ️ No expenses found under account @{active_username} to delete.")
    else:
        choices = {f"{r['expense_date'].strftime('%Y-%m-%d')} • {CATEGORY_ICONS.get(r['category'], '')} {r['title']} ({money(r['amount'])})": r["_id"] for r in user_expenses}
        selected = st.selectbox("Select expense to permanently remove", list(choices.keys()), key="delete_expense_choice")

        st.markdown(
            """
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 10px; padding: 12px 16px; margin: 16px 0;">
                <div style="color: #F87171; font-weight: 600; font-size: 0.9rem;">⚠️ Permanent Action Notice</div>
                <div style="color: #9CA3AF; font-size: 0.8rem; margin-top: 4px;">Once deleted, this transaction document is unrecoverable from your MongoDB ledger.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        confirm = st.checkbox("I confirm I want to permanently delete this expense.")
        if st.button("🗑️ Delete Selected Expense", disabled=not confirm, type="primary", use_container_width=True):
            try:
                result = expenses.delete_one({"_id": choices[selected], "username": active_username})
                if result.deleted_count:
                    st.success("✅ Expense record permanently deleted.")
                    st.rerun()
                else:
                    st.warning("Expense not found or already deleted.")
            except PyMongoError as exc:
                st.error(f"Database error: {exc}")

# ==============================================================================
# TAB 5: MONTHLY BUDGETS (PER-USER BUDGETS)
# ==============================================================================
with tab_budget:
    st.markdown(
        f"""
        <div class="web-panel">
            <div class="panel-header">
                <div class="panel-title">🎯 Set or Update Your Category Budgets (@{active_username})</div>
                <div class="panel-desc">Manage spending limits per category for each month. Unique index per user/month/category prevents collisions.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("budget_form"):
        c1, c2 = st.columns(2)
        budget_month_date = c1.date_input("Choose Target Month", value=date.today().replace(day=1))
        budget_category = c2.selectbox("Category", CATEGORIES, format_func=lambda c: f"{CATEGORY_ICONS.get(c, '')} {c}")
        limit_amount = c1.number_input("Budget Limit (₹) *", min_value=1.0, max_value=10_000_000.0, value=5000.0, step=100.0, format="%.2f")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        save_budget = st.form_submit_button("💾 Save Budget Limit", type="primary", use_container_width=True)

    if save_budget:
        b_key = month_key(budget_month_date)
        try:
            budgets.update_one(
                {"username": active_username, "month": b_key, "category": budget_category},
                {"$set": {"limit": round(float(limit_amount), 2), "updated_at": datetime.utcnow()},
                 "$setOnInsert": {"created_at": datetime.utcnow(), "username": active_username}},
                upsert=True
            )
            st.success(f"✅ Budget saved: {CATEGORY_ICONS.get(budget_category, '')} {budget_category} limit set to {money(limit_amount)} for {b_key} (@{active_username}).")
            st.rerun()
        except PyMongoError as exc:
            st.error(f"Database error: {exc}")

    # Visual Budget Cards & List (Strictly for active_username)
    st.markdown(f"### 📊 Budget Status Cards for @{active_username}")
    active_b_key = month_key(budget_month_date)
    month_budgets = list(budgets.find({"username": active_username, "month": active_b_key}).sort("category", 1))

    if month_budgets:
        # Calculate actual spending for this month for active_username via aggregation
        b_start = datetime(budget_month_date.year, budget_month_date.month, 1)
        b_end = datetime(budget_month_date.year + 1, 1, 1) if budget_month_date.month == 12 else datetime(budget_month_date.year, budget_month_date.month + 1, 1)
        spent_by_cat = {
            item["_id"]: item["total"]
            for item in expenses.aggregate([
                {"$match": {"username": active_username, "expense_date": {"$gte": b_start, "$lt": b_end}}},
                {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}}
            ])
        }

        b_cols = st.columns(min(len(month_budgets), 3))
        for idx, b in enumerate(month_budgets):
            cat = b["category"]
            limit = b["limit"]
            spent = spent_by_cat.get(cat, 0.0)
            pct = min(round((spent / limit) * 100, 1), 100) if limit > 0 else 0
            is_over = spent > limit
            is_warn = (spent / limit) >= 0.75 and not is_over

            badge_class = "budget-badge-danger" if is_over else ("budget-badge-warn" if is_warn else "budget-badge-safe")
            badge_text = "OVER BUDGET" if is_over else (f"{pct}% USED" if is_warn else f"{pct}% USED")
            fill_class = "fill-danger" if is_over else ("fill-warn" if is_warn else "fill-safe")

            with b_cols[idx % 3]:
                st.markdown(
                    f"""
                    <div class="budget-card">
                        <div class="budget-meta">
                            <span class="budget-cat-name">{CATEGORY_ICONS.get(cat, '')} {cat}</span>
                            <span class="{badge_class}">{badge_text}</span>
                        </div>
                        <div class="budget-numbers-row">
                            <span>Spent: <strong>{money(spent)}</strong></span>
                            <span>Limit: {money(limit)}</span>
                        </div>
                        <div class="track">
                            <div class="{fill_class}" style="width: {pct}%;"></div>
                        </div>
                        <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 6px; text-align: right;">
                            {'Deficit: -' + money(spent - limit) if is_over else 'Remaining: ' + money(limit - spent)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown(f"**Your Saved Budgets Table (@{active_username})**")
        all_user_budgets = list(budgets.find({"username": active_username}).sort([("month", -1), ("category", 1)]))
        bdf = pd.DataFrame([{
            "Month": b["month"],
            "Category": f"{CATEGORY_ICONS.get(b['category'], '')} {b['category']}",
            "Budget Limit": f"₹{b['limit']:,.2f}"
        } for b in all_user_budgets])
        st.dataframe(bdf, use_container_width=True, hide_index=True)
    else:
        st.info(f"ℹ️ No budgets saved for {active_b_key} under @{active_username}. Set a budget using the form above!")

# ==============================================================================
# TAB 6: ANALYTICS & REPORTS (USER-ISOLATED MONGODB AGGREGATION)
# ==============================================================================
with tab_reports:
    st.markdown(
        f"""
        <div class="web-panel">
            <div class="panel-header">
                <div class="panel-title">📈 Spending Analytics for @{active_username}</div>
                <div class="panel-desc">Calculated in real-time from your transactions using MongoDB aggregation pipelines</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    r_col1, r_col2 = st.columns([1, 2])
    selected_month = r_col1.date_input("Report Month", value=today.replace(day=1), key="report_month")
    rep_key = month_key(selected_month)
    start = datetime(selected_month.year, selected_month.month, 1)
    end = datetime(selected_month.year + 1, 1, 1) if selected_month.month == 12 else datetime(selected_month.year, selected_month.month + 1, 1)

    # Strictly filter aggregation by active_username
    user_report_match = {"$match": {
        "username": active_username,
        "expense_date": {"$gte": start, "$lt": end}
    }}

    # Aggregation Summary
    total_result = list(expenses.aggregate([
        user_report_match,
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}, "average": {"$avg": "$amount"}}}
    ]))

    total = total_result[0]["total"] if total_result else 0
    count = total_result[0]["count"] if total_result else 0
    average = total_result[0]["average"] if total_result else 0

    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Month Total Spent</div>
                <div class="kpi-val" style="color: #34D399;">{money(total)}</div>
                <div class="kpi-sub">Total spent by @{active_username} in {selected_month.strftime('%B %Y')}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Total Transactions</div>
                <div class="kpi-val">{count}</div>
                <div class="kpi-sub">Your logged records</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Average Per Expense</div>
                <div class="kpi-val">{money(average)}</div>
                <div class="kpi-sub">Mean expenditure</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Aggregation 1: Category Totals for active_username
    category_pipeline = [
        user_report_match,
        {"$group": {"_id": "$category", "total_spent": {"$sum": "$amount"}, "expense_count": {"$sum": 1}}},
        {"$sort": {"total_spent": -1}}
    ]
    category_rows = list(expenses.aggregate(category_pipeline))

    # Aggregation 2: Daily Spending Trend for active_username
    daily_pipeline = [
        user_report_match,
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$expense_date"}}, "total": {"$sum": "$amount"}}},
        {"$sort": {"_id": 1}}
    ]
    daily_rows = list(expenses.aggregate(daily_pipeline))

    # Aggregation 3: Payment Method Totals for active_username
    payment_pipeline = [
        user_report_match,
        {"$group": {"_id": "$payment_method", "total": {"$sum": "$amount"}}},
        {"$sort": {"total": -1}}
    ]
    payment_rows = list(expenses.aggregate(payment_pipeline))

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown(
            f"""
            <div style="font-weight: 700; color: #F9FAFB; margin-bottom: 8px;">
                📊 Spending by Category (@{active_username})
            </div>
            """,
            unsafe_allow_html=True
        )
        if category_rows:
            cat_df = pd.DataFrame([
                {"Category": f"{CATEGORY_ICONS.get(x['_id'], '')} {x['_id']}",
                 "RawCategory": x["_id"],
                 "Total Spent (₹)": round(x["total_spent"], 2),
                 "Transactions": x["expense_count"]}
                for x in category_rows
            ])

            bar_chart = alt.Chart(cat_df).mark_bar(
                cornerRadiusTopRight=6,
                cornerRadiusBottomRight=6,
                color="#10B981"
            ).encode(
                x=alt.X("Total Spent (₹):Q", title="Total Spent (₹)", axis=alt.Axis(gridColor="rgba(255,255,255,0.05)")),
                y=alt.Y("Category:N", title=None, sort="-x"),
                tooltip=["Category", "Total Spent (₹)", "Transactions"]
            ).properties(height=260).configure_view(strokeOpacity=0)

            st.altair_chart(bar_chart, use_container_width=True)
            st.dataframe(cat_df[["Category", "Total Spent (₹)", "Transactions"]], use_container_width=True, hide_index=True)
        else:
            st.info(f"No expenses logged by @{active_username} for {rep_key}.")

    with chart_col2:
        st.markdown(
            f"""
            <div style="font-weight: 700; color: #F9FAFB; margin-bottom: 8px;">
                📈 Daily Spending Trend (@{active_username})
            </div>
            """,
            unsafe_allow_html=True
        )
        if daily_rows:
            daily_df = pd.DataFrame([{"Date": x["_id"], "Amount (₹)": round(x["total"], 2)} for x in daily_rows])

            trend_chart = alt.Chart(daily_df).mark_area(
                line={"color": "#10B981", "size": 2.5},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[
                        alt.GradientStop(color='#10B981', offset=0),
                        alt.GradientStop(color='rgba(16, 185, 129, 0.02)', offset=1)
                    ],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%b %d", gridColor="rgba(255,255,255,0.05)")),
                y=alt.Y("Amount (₹):Q", title="Amount (₹)", axis=alt.Axis(gridColor="rgba(255,255,255,0.05)")),
                tooltip=["Date:T", "Amount (₹):Q"]
            ).properties(height=260).configure_view(strokeOpacity=0)

            st.altair_chart(trend_chart, use_container_width=True)
            st.dataframe(daily_df, use_container_width=True, hide_index=True)
        else:
            st.info(f"No daily spending data recorded by @{active_username} for {rep_key}.")

    # Budget Status Comparison for active_username
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="font-weight: 700; color: #F9FAFB; margin-bottom: 8px;">
            🎯 Budget vs. Actual Spending Comparison (@{active_username})
        </div>
        """,
        unsafe_allow_html=True
    )
    user_month_budgets = list(budgets.find({"username": active_username, "month": rep_key}))
    if user_month_budgets:
        totals_by_category = {x["_id"]: x["total_spent"] for x in category_rows}
        status = []
        for b in user_month_budgets:
            spent = totals_by_category.get(b["category"], 0)
            status.append({
                "Category": f"{CATEGORY_ICONS.get(b['category'], '')} {b['category']}",
                "Budget (₹)": f"₹{b['limit']:,.2f}",
                "Spent (₹)": f"₹{spent:,.2f}",
                "Remaining (₹)": f"₹{b['limit'] - spent:,.2f}",
                "Status": "⚠️ Over budget" if spent > b["limit"] else "✅ Within budget"
            })
        st.dataframe(pd.DataFrame(status), use_container_width=True, hide_index=True)
    else:
        st.info(f"No budgets saved by @{active_username} for {rep_key} yet.")

    # Payment Method Breakdown for active_username
    if payment_rows:
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="font-weight: 700; color: #F9FAFB; margin-bottom: 8px;">
                💳 Spending by Payment Method (@{active_username})
            </div>
            """,
            unsafe_allow_html=True
        )
        pay_df = pd.DataFrame([{"Payment Method": x["_id"], "Total Spent": f"₹{x['total']:,.2f}"} for x in payment_rows])
        st.dataframe(pay_df, use_container_width=True, hide_index=True)

# --- Website Footer ---
st.markdown(
    f"""
    <div class="app-footer">
        <div>
            <strong>ExpensePulse</strong> • Personal Expense Tracker &amp; Budget Analyzer • Signed in as <em>{logged_in_user['full_name']}</em> (@{active_username})
        </div>
        <div class="footer-tags">
            <span class="tag-pill">Python 3.14</span>
            <span class="tag-pill">PyMongo 4.19</span>
            <span class="tag-pill">MongoDB 8.0</span>
            <span class="tag-pill">Streamlit 1.66</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
