"""
=============================================================================
URL SHORTENER - DATABASE LAYER
=============================================================================

This module manages our SQLite database:
1. Opens a connection to 'shortener.db'.
2. Configures row access so columns can be accessed by name (row['original_url']).
3. Creates the 'urls' table with an auto-incrementing primary key ID.
4. shorten_url: Inserts a URL, encodes the ID to Base62, saves the short code.
5. get_url_and_increment_clicks: Looks up a short code via B-Tree index,
   increments click count, and returns the target URL.
6. get_url_stats: Fetches analytics (click counts, created_at timestamp).
=============================================================================
"""

import sqlite3
from typing import Optional, Dict, Any
from encoder import encode_base62

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
    'short_code TEXT UNIQUE' automatically creates a B-Tree index for fast lookups!
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


def shorten_url(original_url: str) -> Dict[str, Any]:
    """
    1. Inserts the original URL to get a unique sequential ID.
    2. Encodes the ID into a Base62 short_code.
    3. Updates the row with the short_code.
    4. Returns the created record.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Step 1: Insert original URL
        cursor.execute(
            "INSERT INTO urls (original_url) VALUES (?)",
            (original_url,)
        )
        url_id = cursor.lastrowid

        # Step 2: Convert ID into Base62
        short_code = encode_base62(url_id)

        # Step 3: Store short_code in the row
        cursor.execute(
            "UPDATE urls SET short_code = ? WHERE id = ?",
            (short_code, url_id)
        )

        return {
            "id": url_id,
            "original_url": original_url,
            "short_code": short_code,
            "clicks": 0
        }


def get_url_and_increment_clicks(short_code: str) -> Optional[str]:
    """
    HOW BACKWARD LOOKUP WORKS:
    1. Queries the database using the B-Tree index on 'short_code'.
    2. If found, increments the 'clicks' counter by 1 atomically.
    3. Returns the original URL so the server can redirect the user.
    4. If not found, returns None.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Step 1: Search using the B-Tree index on short_code
        cursor.execute(
            "SELECT original_url FROM urls WHERE short_code = ?",
            (short_code,)
        )
        row = cursor.fetchone()

        # If code does not exist in our database, return None
        if row is None:
            return None

        # Step 2: Increment click count (+1)
        cursor.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?",
            (short_code,)
        )

        # Step 3: Return the destination URL
        return row["original_url"]


def get_url_stats(short_code: str) -> Optional[Dict[str, Any]]:
    """
    Fetches analytics for a short code:
    - How many times it was clicked
    - When it was created
    - The destination URL
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, original_url, short_code, clicks, created_at
            FROM urls
            WHERE short_code = ?
            """,
            (short_code,)
        )
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None


# =============================================================================
# Verification / Test Run
# =============================================================================
if __name__ == "__main__":
    print("--- Initializing Database ---")
    init_db()

    print("\n1. Shortening a new URL:")
    created = shorten_url("https://www.python.org")
    code = created["short_code"]
    print(f"Created Short Code: '{code}' for {created['original_url']}")

    print(f"\n2. Simulating User Clicking short code '{code}' 3 times:")
    # Click 1
    dest = get_url_and_increment_clicks(code)
    print(f"Click 1 -> Redirect Target: {dest}")

    # Click 2 & 3
    get_url_and_increment_clicks(code)
    get_url_and_increment_clicks(code)

    print(f"\n3. Checking Analytics / Stats for code '{code}':")
    stats = get_url_stats(code)
    print(f"Stats from Database: {stats}")

    print("\n4. Testing a non-existent code 'fake123':")
    missing = get_url_and_increment_clicks("fake123")
    print(f"Result for 'fake123': {missing} (Correctly handled not found!)")
