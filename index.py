import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Initialize data
if "books" not in st.session_state:
    st.session_state["books"] = pd.DataFrame(columns=["Book ID", "Title", "Author", "Genre", "Available Copies", "Total Copies"])

if "borrowed_books" not in st.session_state:
    st.session_state["borrowed_books"] = pd.DataFrame(columns=["Book ID", "Title", "Student Name", "Borrow Date", "Returned"])

if "students_flagged" not in st.session_state:
    st.session_state["students_flagged"] = set()

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
            total_copies = 3
            submitted = st.form_submit_button("Add Book")
            
            if submitted:
                new_book = {
                    "Book ID": book_id,
                    "Title": title,
                    "Author": author,
                    "Genre": genre,
                    "Available Copies": total_copies,
                    "Total Copies": total_copies
                }
                st.session_state.books = st.session_state.books.append(new_book, ignore_index=True)
                st.success("Book added successfully!")
                
    elif choice == "View Borrowed Books":
        st.write("List of Borrowed Books")
        st.write(st.session_state.borrowed_books[st.session_state.borrowed_books["Returned"] == False])
        
    elif choice == "Show All Books":
        st.write("All Books in the Library")
        st.write(st.session_state.books)
        
    elif choice == "Flagged Students":
        st.write("Flagged Students")
        if st.session_state.students_flagged:
            st.write(list(st.session_state.students_flagged))
        else:
            st.write("No flagged students currently.")

# Student functionalities
def student():
    st.title("Student - Library Management System")
    choice = st.sidebar.selectbox("Choose Option", ["Borrow Book", "Return Book", "Show All Books"])
    student_name = st.text_input("Enter Your Name")

    # Check if student is flagged
    if student_name in st.session_state.students_flagged:
        st.warning("You are flagged and cannot borrow books until your fine is cleared.")
        return

    borrowed_books_count = st.session_state.borrowed_books[(st.session_state.borrowed_books["Student Name"] == student_name) & (st.session_state.borrowed_books["Returned"] == False)].shape[0]
    
    if choice == "Borrow Book":
        if borrowed_books_count >= 3:
            st.warning("You have already borrowed the maximum number of books (3).")
        else:
            genre = st.selectbox("Choose Genre", ["Romantic", "Comedy", "Scientific"])
            available_books = st.session_state.books[(st.session_state.books["Genre"] == genre) & (st.session_state.books["Available Copies"] > 0)]
            if not available_books.empty:
                book_id = st.selectbox("Select Book", available_books["Book ID"].tolist())
                if book_id in st.session_state.borrowed_books[(st.session_state.borrowed_books["Student Name"] == student_name) & (st.session_state.borrowed_books["Returned"] == False)]["Book ID"].tolist():
                    st.warning("You already borrowed a copy of this book.")
                else:
                    with st.form("borrow_book_form"):
                        borrow_confirm = st.form_submit_button("Borrow Book")
                        if borrow_confirm:
                            st.session_state.books.loc[st.session_state.books["Book ID"] == book_id, "Available Copies"] -= 1
                            book_info = st.session_state.books[st.session_state.books["Book ID"] == book_id].iloc[0]
                            borrow_date = datetime.now()
                            
                            borrowed_book = {
                                "Book ID": book_id,
                                "Title": book_info["Title"],
                                "Student Name": student_name,
                                "Borrow Date": borrow_date,
                                "Returned": False
                            }
                            st.session_state.borrowed_books = st.session_state.borrowed_books.append(borrowed_book, ignore_index=True)
                            st.success(f"{book_info['Title']} borrowed successfully!")
            else:
                st.warning("No books available in this genre.")
    
    elif choice == "Return Book":
        student_borrowed_books = st.session_state.borrowed_books[
            (st.session_state.borrowed_books["Student Name"] == student_name) & 
            (st.session_state.borrowed_books["Returned"] == False)
        ]
        
        if not student_borrowed_books.empty:
            book_id = st.selectbox("Select Book", student_borrowed_books["Book ID"].tolist())
            with st.form("return_book_form"):
                return_confirm = st.form_submit_button("Return Book")
                if return_confirm:
                    borrow_info = student_borrowed_books[student_borrowed_books["Book ID"] == book_id].iloc[0]
                    borrow_date = borrow_info["Borrow Date"]
                    st.session_state.books.loc[st.session_state.books["Book ID"] == book_id, "Available Copies"] += 1

                    # Check if the book is returned after 7 days
                    if (datetime.now() - borrow_date).days > 7:
                        st.session_state.students_flagged.add(student_name)
                        st.warning("You are flagged due to late return.")
                    else:
                        st.success(f"{borrow_info['Title']} returned successfully!")

                    # Update the borrowed books record
                    st.session_state.borrowed_books.loc[
                        (st.session_state.borrowed_books["Book ID"] == book_id) & 
                        (st.session_state.borrowed_books["Student Name"] == student_name), 
                        "Returned"] = True
                    
        else:
            st.warning("You have no borrowed books to return.")
    
    elif choice == "Show All Books":
        st.write("All Books in the Library")
        st.write(st.session_state.books)

# Main function to control the flow
def main():
    st.sidebar.title("Library Management System")
    user_type = st.sidebar.selectbox("Select User Type", ["Admin", "Student"])
    
    if user_type == "Admin":
        admin()
    else:
        student()

if __name__ == "__main__":
    main()
