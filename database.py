"""
=============================================================================
URL SHORTENER - DATABASE LAYER
=============================================================================

This module manages our SQLite database:
1. Opens a connection to the database file ('shortener.db').
2. Configures row access so columns can be accessed by name (like a dictionary).
3. Creates the 'urls' table with an auto-incrementing primary key ID.
4. shorten_url: Inserts a URL, gets its auto-generated ID, encodes it into Base62,
   and saves the short code.
=============================================================================
"""

import sqlite3
from encoder import encode_base62

# The name of our database file on disk.
DB_NAME = "shortener.db"


def get_connection():
    """
    Opens and returns a connection to our SQLite database.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Creates the 'urls' table if it does not already exist.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT UNIQUE,
                clicks INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


def shorten_url(original_url: str) -> dict:
    """
    Shortens a long URL through 4 steps:
    1. Inserts the long URL into SQLite (to get a unique sequential ID).
    2. Reads the generated ID using cursor.lastrowid.
    3. Converts that ID into a Base62 string using encode_base62().
    4. Updates the row with the newly generated short_code.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Step 1: Insert the long URL into the database
        cursor.execute(
            "INSERT INTO urls (original_url) VALUES (?)",
            (original_url,)
        )

        # Step 2: Grab the unique auto-incremented ID assigned by SQLite
        url_id = cursor.lastrowid

        # Step 3: Convert that number to a Base62 short code (e.g. 1 -> "1", 200 -> "3e")
        short_code = encode_base62(url_id)

        # Step 4: Update the row with its short code
        cursor.execute(
            "UPDATE urls SET short_code = ? WHERE id = ?",
            (short_code, url_id)
        )

        # Return a dictionary with the saved details
        return {
            "id": url_id,
            "original_url": original_url,
            "short_code": short_code,
            "clicks": 0
        }


# Test the database operations
if __name__ == "__main__":
    print("--- Initializing Database ---")
    init_db()

    print("\n--- Testing URL Shortening ---")
    new_url = shorten_url("https://www.wikipedia.org")
    print(f"Created Record: {new_url}")

    new_url_2 = shorten_url("https://github.com/ahasraajvv/URL--shortner-")
    print(f"Created Record: {new_url_2}")
