import sqlite3
# Database setup function
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    # Create table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, 
            password TEXT, 
            role TEXT
        )
    ''')
    conn.commit()
    conn.close()
init_db()