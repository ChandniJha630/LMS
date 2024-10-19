import streamlit as st
import sqlite3
from .admin2 import admin
from .student import student

# Function to add a new user
def save_user(username, password, role):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
              (username, password, role))
    conn.commit()
    conn.close()

# Function to validate login
def login(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

# Function to check if a user already exists
def user_exists(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Authentication function with Streamlit UI
def Auth():

    # Initialize session state for user login if not already done
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None

    # If user is logged in, show welcome message and redirect to role-based dashboard
    if st.session_state.logged_in:
        st.sidebar.write(f"Welcome, {st.session_state.username}!")

        # Automatically display the respective dashboard based on user role
        if st.session_state.user_role == "admin":
            admin()
        elif st.session_state.user_role == "student":
            student()

        # Logout button
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.username = None
            st.success("You have successfully logged out.")
            st.experimental_rerun()  # Force rerun to go back to login/register page

    else:
        # If user is not logged in, show login/register options
        option = st.sidebar.selectbox("Select an Option", ["Login", "Register"])

        # If user chooses Login
        if option == "Login":
            st.header("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.button("Login")

            if login_button:
                user_role = login(username, password)
                if user_role:
                    st.session_state.logged_in = True
                    st.session_state.user_role = user_role
                    st.session_state.username = username
                    st.success(f"Welcome, {username}!")
                    st.experimental_rerun()  # Redirect to the appropriate dashboard
                else:
                    st.error("Invalid username or password.")

        # If user chooses Register
        elif option == "Register":
            st.header("Register")
            reg_username = st.text_input("New Username")
            reg_password = st.text_input("New Password", type="password")
            reg_role = st.selectbox("Role", ["student", "admin"])
            register_button = st.button("Register")

            if register_button:
                if reg_username and reg_password:
                    if user_exists(reg_username):
                        st.error("Username already exists. Please choose a different one.")
                    else:
                        save_user(reg_username, reg_password, reg_role)
                        st.success("Registration successful. You can now log in.")
                else:
                    st.error("Please fill in all fields for registration.")

