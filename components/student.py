import streamlit as st
from datetime import datetime
import sqlite3
import pandas as pd
from .admin2 import get_all_books


# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn

# Fetch flagged students
def get_flagged_students():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT student_id FROM flagged_students")
    flagged_students = [row["student_id"] for row in c.fetchall()]
    conn.close()
    return flagged_students

def borrow_book(student_id, book_id):
    conn = get_db_connection()
    c = conn.cursor()

    # Retrieve the book title based on book_id
    c.execute("SELECT title FROM books WHERE book_id = ?", (book_id,))
    book = c.fetchone()

    if not book:
        st.error("Book not found.")
        conn.close()
        return
    
    book_title = book[0]  # Fetch the title from the tuple

    # Update available copies in books table
    c.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?", (book_id,))
    
    # Add to borrowed_books table
    borrow_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format the date as string
    c.execute("INSERT INTO borrowed_books (book_id, student_id, borrow_date, returned) VALUES (?, ?, ?, ?)",
              (book_id, student_id, borrow_date, 0))  # Only pass necessary parameters

    conn.commit()
    conn.close()

# Retrieve available books by genre
def get_available_books_by_genre(genre):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Query to get available books of the specified genre
    c.execute("SELECT * FROM books WHERE genre = ? AND available_copies > 0", (genre,))
    available_books = c.fetchall()
    
    conn.close()
    return available_books
# Retrieve borrowed books by a specific student
def get_borrowed_books_by_student(student_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Query to get books borrowed by the student
    c.execute("SELECT * FROM borrowed_books WHERE student_id = ?", (student_id,))
    borrowed_books = c.fetchall()
    
    conn.close()
    return borrowed_books

# Return a book
from datetime import datetime

def flag_student(student_id):
    conn = get_db_connection()
    c = conn.cursor()

    # Check if the student is already flagged
    c.execute("SELECT * FROM flagged_students WHERE student_id = ?", (student_id,))
    if c.fetchone() is None:
        # Insert a new record if not already flagged
        c.execute("INSERT INTO flagged_students (student_id) VALUES (?)", (student_id,))
    else:
        # If the student is already flagged, you can choose to handle it differently
        # For example, you could update the flagged status or leave it as is
        st.warning("Student is already flagged.")
    
    conn.commit()
    conn.close()



def return_book(student_id, book_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get the borrow date to calculate late return
    c.execute("SELECT borrow_date FROM borrowed_books WHERE book_id = ? AND student_id = ? AND returned = 0", (book_id, student_id))
    borrow_info = c.fetchone()
    
    if borrow_info:
        borrow_date = datetime.strptime(borrow_info[0], "%Y-%m-%d %H:%M:%S")  # Use [0] to access the value
        
        # Update available copies in books table
        c.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?", (book_id,))
        
        # Check for late return
        return_date = datetime.now()
        if (return_date - borrow_date).days > 1:
            flag_student(student_id)  # Flag student for late return
            st.warning("You are flagged due to late return.")
        else:
            st.success("Book returned successfully!")
        
        # Update borrowed_books record with return date
        c.execute("UPDATE borrowed_books SET returned = 1, return_date = ? WHERE book_id = ? AND student_id = ?", 
                  (return_date.strftime("%Y-%m-%d %H:%M:%S"), book_id, student_id))
        
        conn.commit()
    else:
        st.error("You haven't borrowed this book or it has already been returned.")
    
    conn.close()



# Student functionalities
def student():
    st.title("Student - Library Management System")
    choice = st.sidebar.selectbox("Choose Option", ["Borrow Book", "Return Book", "Show All Books"])

    if choice == "Borrow Book":
        student_id = st.number_input("Enter Your ID", min_value=0)
        
        # Get the count of borrowed books for the student
         # Ensure this function is defined
        borrowed_books = get_borrowed_books_by_student(student_id)
        currently_borrowed_ids = [
                    book["book_id"] for book in borrowed_books if book["returned"] == 0
                ]

        borrowed_books_count=len(currently_borrowed_ids)
        if borrowed_books_count >= 3:
            st.warning("You have already borrowed the maximum number of books (3).")
        else:
            genre = st.selectbox("Choose Genre", ["Romantic", "Comedy", "Scientific"])
            available_books = get_available_books_by_genre(genre)  # Ensure this function is defined

            if available_books:
                book_id = st.selectbox("Select Book", [book["book_id"] for book in available_books])

                # Check if the book is already borrowed by the student
                borrowed_books = get_borrowed_books_by_student(student_id)
                currently_borrowed_ids = [
                    book["book_id"] for book in borrowed_books if book["returned"] == 0
                ]

                if book_id in currently_borrowed_ids:
                    st.warning("You have already borrowed a copy of this book.")
                else:
                    with st.form("borrow_book_form"):
                        borrow_confirm = st.form_submit_button("Borrow Book")
                        if borrow_confirm:
                            # Call the borrow_book function
                            borrow_book(student_id, book_id)  # Pass only student_id and book_id
                            st.success(f"{next(book['title'] for book in available_books if book['book_id'] == book_id)} borrowed successfully!")
            else:
                st.warning("No books available in this genre.")

    
    elif choice == "Return Book":
        # Get the list of borrowed books for the student
        student_id = st.number_input("Enter Your ID", min_value=0)
        student_borrowed_books = get_borrowed_books_by_student(student_id)  # Ensure this function is defined
        
        if not student_borrowed_books:
            st.warning("You have not borrowed any books.")
        else:
            book_id = st.selectbox("Select Book to Return", [book["book_id"] for book in student_borrowed_books])

            if st.button("Return Book"):
                return_book(student_id, book_id) 
    
    elif choice == "Show All Books":
        st.write("All Books in the Library")
        books = get_all_books()
        if books:
            df_books = pd.DataFrame(books, columns=["Book ID", "Title", "Author", "Genre", "Available Copies", "Total Copies"])
            st.dataframe(df_books)
        else:
            st.write("No books in the library.")
