import sqlite3

def create_connection():
    conn = sqlite3.connect('library.db')
    return conn

def create_tables():
    connection = create_connection()
    cursor = connection.cursor()

    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL
        )
    ''')

    # Create books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            available_copies INTEGER DEFAULT 3,
            total_copies INTEGER DEFAULT 3
        )
    ''')

    # Create borrowed_books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrowed_books (
            borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            student_id INTEGER,
            borrow_date TEXT,
            return_date TEXT,
            returned INTEGER DEFAULT 0,
            FOREIGN KEY (book_id) REFERENCES books(book_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')

    # Create flagged_students table
    # Create the flagged_students table with a flagged status
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flagged (
            student_id INTEGER PRIMARY KEY,
            flagged INTEGER DEFAULT 1
        )
    ''')


    connection.commit()
    connection.close()
    print("Tables created successfully.")

def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn

def get_borrowed_books_by_student(student_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Query to get books borrowed by the student
    c.execute("SELECT * FROM borrowed_books WHERE student_id = ?", (student_id,))
    borrowed_books = c.fetchall()
    
    conn.close()
    import pandas as pd
    df_borrowed_books = pd.DataFrame(borrowed_books, columns=["Borrower ID", "Student ID", "Book ID", "Borrow Date", "Return Date", "Returned"])
    print(df_borrowed_books)
    
get_borrowed_books_by_student(0)