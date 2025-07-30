"""
Database schema definition for the Library Management System.

This module contains SQL statements for creating and managing the database schema.
"""

import sqlite3
from typing import Optional


# Schema version for database migrations
SCHEMA_VERSION = "1.0.0"

# SQL statements for creating tables
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN ('Member', 'Staff')),
    phone TEXT,
    staff_role TEXT,
    department TEXT,
    hire_date TEXT,
    registration_date TEXT NOT NULL,
    membership_expiry TEXT,
    fines_owed REAL DEFAULT 0.0,
    is_active BOOLEAN DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS items (
    item_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    item_type TEXT NOT NULL CHECK (item_type IN ('Book', 'Magazine', 'DVD')),
    is_available BOOLEAN DEFAULT 1,
    date_added TEXT NOT NULL,
    -- Book-specific fields
    author TEXT,
    isbn TEXT,
    pages INTEGER,
    -- Magazine-specific fields
    issue_number TEXT,
    publisher TEXT,
    publication_date TEXT,
    -- DVD-specific fields
    duration INTEGER,
    genre TEXT,
    director TEXT,
    rating TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_LOANS_TABLE = """
CREATE TABLE IF NOT EXISTS loans (
    loan_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    date_borrowed TEXT NOT NULL,
    date_due TEXT NOT NULL,
    date_returned TEXT,
    is_returned BOOLEAN DEFAULT 0,
    fine_amount REAL DEFAULT 0.0,
    renewal_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (item_id) REFERENCES items (item_id)
);
"""

CREATE_SYSTEM_INFO_TABLE = """
CREATE TABLE IF NOT EXISTS system_info (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

# Indexes for better performance
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
    "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);",
    "CREATE INDEX IF NOT EXISTS idx_items_type ON items(item_type);",
    "CREATE INDEX IF NOT EXISTS idx_items_available ON items(is_available);",
    "CREATE INDEX IF NOT EXISTS idx_items_title ON items(title);",
    "CREATE INDEX IF NOT EXISTS idx_loans_user_id ON loans(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_loans_item_id ON loans(item_id);",
    "CREATE INDEX IF NOT EXISTS idx_loans_returned ON loans(is_returned);",
    "CREATE INDEX IF NOT EXISTS idx_loans_due_date ON loans(date_due);",
]

# Triggers for automatic timestamp updates
CREATE_TRIGGERS = [
    """
    CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
    AFTER UPDATE ON users
    FOR EACH ROW
    BEGIN
        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE user_id = NEW.user_id;
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS update_items_timestamp 
    AFTER UPDATE ON items
    FOR EACH ROW
    BEGIN
        UPDATE items SET updated_at = CURRENT_TIMESTAMP WHERE item_id = NEW.item_id;
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS update_loans_timestamp 
    AFTER UPDATE ON loans
    FOR EACH ROW
    BEGIN
        UPDATE loans SET updated_at = CURRENT_TIMESTAMP WHERE loan_id = NEW.loan_id;
    END;
    """
]


def create_tables(connection: sqlite3.Connection) -> None:
    """
    Create all necessary tables and indexes in the database.
    
    Args:
        connection: SQLite database connection
    """
    cursor = connection.cursor()
    
    try:
        # Create tables
        cursor.execute(CREATE_USERS_TABLE)
        cursor.execute(CREATE_ITEMS_TABLE)
        cursor.execute(CREATE_LOANS_TABLE)
        cursor.execute(CREATE_SYSTEM_INFO_TABLE)
        
        # Create indexes
        for index_sql in CREATE_INDEXES:
            cursor.execute(index_sql)
        
        # Create triggers
        for trigger_sql in CREATE_TRIGGERS:
            cursor.execute(trigger_sql)
        
        # Insert schema version
        cursor.execute(
            "INSERT OR REPLACE INTO system_info (key, value) VALUES (?, ?)",
            ("schema_version", SCHEMA_VERSION)
        )
        
        connection.commit()
        print(f"Database schema created successfully (version {SCHEMA_VERSION})")
        
    except sqlite3.Error as e:
        connection.rollback()
        raise Exception(f"Failed to create database schema: {e}")


def get_schema_version(connection: sqlite3.Connection) -> Optional[str]:
    """
    Get the current schema version from the database.
    
    Args:
        connection: SQLite database connection
        
    Returns:
        Schema version string or None if not found
    """
    cursor = connection.cursor()
    
    try:
        cursor.execute(
            "SELECT value FROM system_info WHERE key = ?",
            ("schema_version",)
        )
        result = cursor.fetchone()
        return result[0] if result else None
        
    except sqlite3.Error:
        return None


def drop_all_tables(connection: sqlite3.Connection) -> None:
    """
    Drop all tables from the database (useful for testing).
    
    Args:
        connection: SQLite database connection
    """
    cursor = connection.cursor()
    
    try:
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Drop all tables
        for table in tables:
            if table[0] != 'sqlite_sequence':  # Don't drop SQLite internal table
                cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
        
        connection.commit()
        print("All tables dropped successfully")
        
    except sqlite3.Error as e:
        connection.rollback()
        raise Exception(f"Failed to drop tables: {e}")


def reset_database(connection: sqlite3.Connection) -> None:
    """
    Reset the database by dropping and recreating all tables.
    
    Args:
        connection: SQLite database connection
    """
    drop_all_tables(connection)
    create_tables(connection) 