import sqlite3

def initialize_database():
    conn = sqlite3.connect('media_records.db')
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            image_path TEXT NOT NULL,
            audio_path TEXT,
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == "__main__":
    initialize_database()
