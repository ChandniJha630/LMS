import pytest
from unittest.mock import MagicMock, patch
from components.admin2 import add_book, get_all_books, get_db_connection
from components.student import get_available_books_by_genre, get_borrowed_books_by_student, flag_student, return_book, borrow_book, get_db_connection

@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.patch('sqlite3.connect')
    mock_cursor = mock_conn.return_value.cursor.return_value
    mock_conn.return_value.commit.return_value = None
    return mock_cursor





def test_add_book_successful(mock_db):
    book_id = "B001"
    title = "Python Programming"
    author = "John Doe"
    genre = "Scientific"
    total_copies = 3
    
    add_book(book_id, title, author, genre, total_copies, total_copies)
    
    mock_db.execute.assert_called_once_with(
        "INSERT INTO books (book_id, title, author, genre, available_copies, total_copies) VALUES (?, ?, ?, ?, ?, ?)",
        (book_id, title, author, genre, total_copies, total_copies)
    )
    print("Test add_book_successful passed!")

def test_add_book_missing_arguments(mock_db):
    book_id = "B002"
    title = "Java Programming"
    
    with pytest.raises(TypeError):
        add_book(book_id, title)
    print("Test add_book_missing_arguments passed!")

def test_add_book_multiple_calls(mock_db):
    book_id = "B003"
    title = "JavaScript Essentials"
    author = "Jane Roe"
    genre = "Web Development"
    total_copies = 5
    
    add_book(book_id, title, author, genre, total_copies, total_copies)
    add_book(book_id, title, author, genre, total_copies, total_copies)
    
    assert mock_db.execute.call_count == 2
    print("Test add_book_multiple_calls passed!")

def test_get_all_books(mock_db):
    mock_db.fetchall.return_value = [
        {"book_id": "B001", "title": "Python Programming", "author": "John Doe", "genre": "Scientific", "available_copies": 3, "total_copies": 3},
        {"book_id": "B002", "title": "Data Science", "author": "Jane Doe", "genre": "Scientific", "available_copies": 2, "total_copies": 3}
    ]
    
    books = get_all_books()
    
    mock_db.execute.assert_called_once_with("SELECT * FROM books")
    
    assert len(books) == 2
    assert books[0]["title"] == "Python Programming"
    print("Test get_all_books passed!")

from datetime import datetime

def test_borrow_book(mock_db, mocker):
    student_id = "S001"
    book_id = "B001"
    
    mock_db.fetchone.return_value = ("Python Programming",)
    
    mock_now = mocker.patch('components.student.datetime')
    mock_now.now.return_value = datetime(2024, 10, 15)
    
    borrow_book(student_id, book_id)
    
    mock_db.execute.assert_any_call("SELECT title FROM books WHERE book_id = ?", (book_id,))
    mock_db.execute.assert_any_call("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?", (book_id,))
    mock_db.execute.assert_any_call(
        "INSERT INTO borrowed_books (book_id, student_id, borrow_date, returned) VALUES (?, ?, ?, ?)",
        (book_id, student_id, "2024-10-15 00:00:00", 0)
    )
    print("Test borrow_book passed!")
   

def test_return_book(mock_db, mocker):
    student_id = "S001"
    book_id = "B001"

    # Mock fetching the borrow date (if needed for any logic in the return)
    mock_db.fetchone.return_value = ("2024-10-01",)  # Assuming borrow date is fetched first

    # Mock date for the return action
    mock_now = mocker.patch('components.student.datetime')
    mock_now.now.return_value = datetime(2024, 10, 15)

    # Call the return_book function
    return_book(student_id, book_id)
   
    # Verify the SQL commands
    mock_db.execute.assert_any_call(
        "UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?",
        (book_id,)
    )
   
    mock_db.execute.assert_any_call(
        "UPDATE borrowed_books SET returned = 1, return_date = ? WHERE book_id = ? AND student_id = ?",
        ("2024-10-15 00:00:00", book_id, student_id)
    )
    print("Test return_book passed!")




def test_flag_student(mock_db):
    cursor = mock_db.cursor()
    cursor.execute("CREATE TABLE flagged_students (student_id INTEGER)")
    
    flag_student(123)
    
    cursor.execute("SELECT student_id FROM flagged_students WHERE student_id = 123")
    assert cursor.fetchone() is not None
    print("Test flag_student passed!")
