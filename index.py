import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from components.auth import Auth

# Initialize data
if "books" not in st.session_state:
    st.session_state["books"] = pd.DataFrame(columns=["Book ID", "Title", "Author", "Genre", "Available Copies", "Total Copies"])

if "borrowed_books" not in st.session_state:
    st.session_state["borrowed_books"] = pd.DataFrame(columns=["Book ID", "Title", "Student Name", "Borrow Date", "Returned"])

if "students_flagged" not in st.session_state:
    st.session_state["students_flagged"] = set()

# Main function to control the flow
def main():
    st.sidebar.title("Library Management System")
    Auth()

if __name__ == "__main__":
    main()
