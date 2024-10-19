import streamlit as st
import sqlite3
import pandas as pd

# Function to connect to the database
def get_db_connection():
    try:
        conn = sqlite3.connect('library.db')
        conn.row_factory = sqlite3.Row  # Enable row factory to access columns by name
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Initialize database and create necessary tables
def initialize_database():
    conn = get_db_connection()
    if conn is not None:
        c = conn.cursor()
        # Create books table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT NOT NULL,
                available_copies INTEGER NOT NULL,
                total_copies INTEGER NOT NULL
            )
        ''')
        # Create borrowed_books table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS borrowed_books (
                borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                book_id TEXT NOT NULL,
                borrow_date TEXT NOT NULL,
                return_date TEXT,
                returned INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (book_id) REFERENCES books (book_id)
            )
        ''')
        # Create flagged table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS flagged (
                student_id TEXT PRIMARY KEY
            )
        ''')
        conn.commit()
        conn.close()

# Add book to database
def add_book(book_id, title, author, genre, available_copies, total_copies):
    conn = get_db_connection()
    if conn:
        c = conn.cursor()
        c.execute("INSERT INTO books (book_id, title, author, genre, available_copies, total_copies) VALUES (?, ?, ?, ?, ?, ?)",
                  (book_id, title, author, genre, available_copies, total_copies))
        conn.commit()
        conn.close()

# Retrieve all books from database
def get_all_books():
    conn = get_db_connection()
    if conn:
        c = conn.cursor()
        c.execute("SELECT * FROM books")
        books = c.fetchall()
        conn.close()
        return books
    return []

# Retrieve borrowed books from database
def get_borrowed_books():
    conn = get_db_connection()
    if conn:
        c = conn.cursor()
        c.execute("SELECT borrow_id, student_id, book_id, borrow_date, return_date, returned FROM borrowed_books")
        books = c.fetchall()
        conn.close()
        return books
    return []

# Retrieve flagged students from database
def get_flagged_students():
    conn = get_db_connection()
    if conn:
        c = conn.cursor()
        c.execute("SELECT student_id FROM flagged")
        students = [row["student_id"] for row in c.fetchall()]
        conn.close()
        return students
    return []

# Flag a student
def flag_student(student_id):
    conn = get_db_connection()
    if conn:
        c = conn.cursor()
        c.execute("INSERT INTO flagged (student_id) VALUES (?)", (student_id,))
        conn.commit()
        conn.close()

# Admin functionalities
def admin():
    st.title("Admin - Library Management System")
    choice = st.sidebar.selectbox("Choose Option", ["Add Book", "View Borrowed Books", "Show All Books", "Flagged Students"])

    if choice == "Add Book":
        with st.form("add_book_form"):
            book_id = st.text_input("Book ID")
            title = st.text_input("Title")
            author = st.text_input("Author")
            genre = st.selectbox("Genre", ["Romantic", "Comedy", "Scientific"])
            total_copies = 3  # Fixed number of copies
            submitted = st.form_submit_button("Add Book")

        if submitted:
            # Validate input
            if not book_id or not title or not author:
                st.error("Please fill in all fields.")
            else:
                # Check if book already exists
                existing_books = get_all_books()
                if any(book["book_id"] == book_id for book in existing_books):
                    st.error("A book with this ID already exists.")
                else:
                    # Call add_book with the correct number of arguments
                    add_book(book_id, title, author, genre, total_copies, total_copies)
                    st.success("Book added successfully!")

    elif choice == "View Borrowed Books":
        st.write("List of Borrowed Books")
        borrowed_books = get_borrowed_books()
        if borrowed_books:
            df_borrowed_books = pd.DataFrame(borrowed_books, columns=["Borrower ID", "Student ID", "Book ID", "Borrow Date", "Return Date", "Returned"])
            st.dataframe(df_borrowed_books)
        else:
            st.write("No borrowed books to display.")

    elif choice == "Show All Books":
        st.write("All Books in the Library")
        books = get_all_books()
        if books:
            df_books = pd.DataFrame(books, columns=["Book ID", "Title", "Author", "Genre", "Available Copies", "Total Copies"])
            st.dataframe(df_books)
        else:
            st.write("No books in the library.")

    elif choice == "Flagged Students":
        st.write("Flagged Students")
        students = get_flagged_students()
        if students:
            st.write(students)
        else:
            st.write("No flagged students currently.")

