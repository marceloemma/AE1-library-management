"""
Database manager for the Library Management System.

This module provides the DatabaseManager class which handles all database
operations and serves as an interface between the object model and SQLite.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import sys
import os
        # need this for imports to work properly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.abstract_classes import LibraryItem, User
from models.items import Book, Magazine, DVD
from models.users import Member, Staff
from models.loan import Loan
from .schema import create_tables, get_schema_version, SCHEMA_VERSION


class DatabaseManager:
    """
    Handles all database operations. 
    
    Saves/loads users, items, and loans to/from SQLite.
    """
    
    def __init__(self, db_path: str = "library.db"):
        """
        Initialise the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        self._ensure_database_exists()
    
    def _ensure_database_exists(self) -> None:
        """Ensure the database file and schema exist."""
        # Create database directory if it doesn't exist
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect and create schema if needed
        with self.get_connection() as conn:
            current_version = get_schema_version(conn)
            if current_version != SCHEMA_VERSION:
                create_tables(conn)
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection.
        
        Returns:
            SQLite connection object
        """
        if self._connection is None or self._connection.execute("PRAGMA table_info(users)").fetchone() is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row  # Enable dict-like access to rows
        
        return self._connection
    
    def close_connection(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    # User Management Methods
    def save_user(self, user: User) -> bool:
        """
        Save a user to the database.
        
        Args:
            user: User object to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Prepare user data based on type
                base_data = {
                    'user_id': user.user_id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.get_role(),
                    'registration_date': user.registration_date.isoformat()
                }
                
                if isinstance(user, Member):
                                    user_data = {
                    **base_data,
                    'phone': user.phone,
                    'membership_expiry': user.membership_expiry.isoformat(),
                    'fines_owed': user.fines_owed,
                    'staff_role': None,
                    'department': None,
                    'hire_date': None
                }
                elif isinstance(user, Staff):
                                    user_data = {
                    **base_data,
                    'phone': None,
                    'membership_expiry': None,
                    'fines_owed': 0.0,
                    'staff_role': user.staff_role,
                    'department': None,
                    'hire_date': user.hire_date.isoformat()
                }
                else:
                    return False
                
                # Insert or update user
                cursor.execute("""
                    INSERT OR REPLACE INTO users 
                    (user_id, name, email, role, phone, staff_role, 
                     department, hire_date, registration_date, membership_expiry, fines_owed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data['user_id'], user_data['name'], user_data['email'],
                    user_data['role'], user_data['phone'],
                    user_data['staff_role'], user_data['department'], user_data['hire_date'],
                    user_data['registration_date'], user_data['membership_expiry'],
                    user_data['fines_owed']
                ))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            print(f"Error saving user: {e}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve a user by ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            User object or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return self._row_to_user(row)
                
        except sqlite3.Error as e:
            print(f"Error retrieving user: {e}")
            return None
    
    def get_all_users(self) -> List[User]:
        """
        Retrieve all users from the database.
        
        Returns:
            List of User objects
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users ORDER BY name")
                rows = cursor.fetchall()
                
                return [self._row_to_user(row) for row in rows]
                
        except sqlite3.Error as e:
            print(f"Error retrieving users: {e}")
            return []
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from the database.
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            print(f"Error deleting user: {e}")
            return False
    
    def _row_to_user(self, row: sqlite3.Row) -> User:
        """Convert a database row to a User object."""
        if row['role'] == 'Member':
            user = Member(
                user_id=row['user_id'],
                name=row['name'],
                email=row['email'],
                phone=row['phone']
            )
            
            # Set additional member properties
            if row['membership_expiry']:
                user._membership_expiry = datetime.fromisoformat(row['membership_expiry'])
            user._fines_owed = row['fines_owed'] or 0.0
            
        elif row['role'] == 'Staff':
            hire_date = None
            if row['hire_date']:
                hire_date = datetime.fromisoformat(row['hire_date'])
            
            user = Staff(
                user_id=row['user_id'],
                name=row['name'],
                email=row['email'],
                role=row['staff_role'] or 'Librarian',
                hire_date=hire_date
            )
        else:
            raise ValueError(f"Unknown user role: {row['role']}")
        
        # Set registration date
        if row['registration_date']:
            user._registration_date = datetime.fromisoformat(row['registration_date'])
        
        return user
    
    # Item Management Methods
    def save_item(self, item: LibraryItem) -> bool:
        """
        Save an item to the database.
        
        Args:
            item: LibraryItem object to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Prepare base item data
                base_data = {
                    'item_id': item.item_id,
                    'title': item.title,
                    'item_type': item.get_item_type(),
                    'is_available': item.is_available,
                    'date_added': item.date_added.isoformat()
                }
                
                # Add type-specific data
                if isinstance(item, Book):
                    item_data = {
                        **base_data,
                        'author': item.author,
                        'isbn': item.isbn,
                        'pages': item.pages,
                        'issue_number': None,
                        'publisher': None,
                        'publication_date': None,
                        'duration': None,
                        'genre': None,
                        'director': None,
                        'rating': None
                    }
                elif isinstance(item, Magazine):
                    item_data = {
                        **base_data,
                        'author': None,
                        'isbn': None,
                        'pages': None,
                        'issue_number': item.issue_number,
                        'publisher': item.publisher,
                        'publication_date': item.publication_date.isoformat(),
                        'duration': None,
                        'genre': None,
                        'director': None,
                        'rating': None
                    }
                elif isinstance(item, DVD):
                    item_data = {
                        **base_data,
                        'author': None,
                        'isbn': None,
                        'pages': None,
                        'issue_number': None,
                        'publisher': None,
                        'publication_date': None,
                        'duration': item.duration,
                        'genre': item.genre,
                        'director': item.director,
                        'rating': item.rating
                    }
                else:
                    return False
                
                # Insert or update item
                cursor.execute("""
                    INSERT OR REPLACE INTO items 
                    (item_id, title, item_type, is_available, date_added, author, isbn, pages,
                     issue_number, publisher, publication_date, duration, genre, director, rating)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_data['item_id'], item_data['title'], item_data['item_type'],
                    item_data['is_available'], item_data['date_added'], item_data['author'],
                    item_data['isbn'], item_data['pages'], item_data['issue_number'],
                    item_data['publisher'], item_data['publication_date'], item_data['duration'],
                    item_data['genre'], item_data['director'], item_data['rating']
                ))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            print(f"Error saving item: {e}")
            return False
    
    def get_item_by_id(self, item_id: str) -> Optional[LibraryItem]:
        """
        Retrieve an item by ID.
        
        Args:
            item_id: ID of the item to retrieve
            
        Returns:
            LibraryItem object or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM items WHERE item_id = ?", (item_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return self._row_to_item(row)
                
        except sqlite3.Error as e:
            print(f"Error retrieving item: {e}")
            return None
    
    def get_all_items(self) -> List[LibraryItem]:
        """
        Retrieve all items from the database.
        
        Returns:
            List of LibraryItem objects
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM items ORDER BY title")
                rows = cursor.fetchall()
                
                return [self._row_to_item(row) for row in rows]
                
        except sqlite3.Error as e:
            print(f"Error retrieving items: {e}")
            return []
    
    def search_items(self, query: str) -> List[LibraryItem]:
        """
        Search for items by title.
        
        Args:
            query: Search query
            
        Returns:
            List of matching LibraryItem objects
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM items WHERE title LIKE ? ORDER BY title",
                    (f"%{query}%",)
                )
                rows = cursor.fetchall()
                
                return [self._row_to_item(row) for row in rows]
                
        except sqlite3.Error as e:
            print(f"Error searching items: {e}")
            return []
    
    def delete_item(self, item_id: str) -> bool:
        """
        Delete an item from the database.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM items WHERE item_id = ?", (item_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            print(f"Error deleting item: {e}")
            return False
    
    def _row_to_item(self, row: sqlite3.Row) -> LibraryItem:
        """Convert a database row to a LibraryItem object."""
        if row['item_type'] == 'Book':
            item = Book(
                item_id=row['item_id'],
                title=row['title'],
                author=row['author'] or '',
                isbn=row['isbn'] or '',
                pages=row['pages'] or 0
            )
        elif row['item_type'] == 'Magazine':
            pub_date = None
            if row['publication_date']:
                pub_date = datetime.fromisoformat(row['publication_date'])
            
            item = Magazine(
                item_id=row['item_id'],
                title=row['title'],
                issue_number=row['issue_number'] or '',
                publisher=row['publisher'] or '',
                publication_date=pub_date
            )
        elif row['item_type'] == 'DVD':
            item = DVD(
                item_id=row['item_id'],
                title=row['title'],
                duration=row['duration'] or 0,
                genre=row['genre'] or '',
                director=row['director'],
                rating=row['rating']
            )
        else:
            raise ValueError(f"Unknown item type: {row['item_type']}")
        
        # Set common properties
        item._is_available = bool(row['is_available'])
        if row['date_added']:
            item._date_added = datetime.fromisoformat(row['date_added'])
        
        return item
    
    # Loan Management Methods
    def save_loan(self, loan: Loan) -> bool:
        """
        Save a loan to the database.
        
        Args:
            loan: Loan object to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO loans 
                    (loan_id, user_id, item_id, date_borrowed, date_due, date_returned,
                     is_returned, fine_amount, renewal_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    loan.loan_id, loan.user_id, loan.item_id,
                    loan.date_borrowed.isoformat(), loan.date_due.isoformat(),
                    loan.date_returned.isoformat() if loan.date_returned else None,
                    loan.is_returned, loan.fine_amount, loan.renewal_count
                ))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            print(f"Error saving loan: {e}")
            return False
    
    def get_loan_by_id(self, loan_id: str) -> Optional[Loan]:
        """
        Retrieve a loan by ID.
        
        Args:
            loan_id: ID of the loan to retrieve
            
        Returns:
            Loan object or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM loans WHERE loan_id = ?", (loan_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return self._row_to_loan(row)
                
        except sqlite3.Error as e:
            print(f"Error retrieving loan: {e}")
            return None
    
    def get_loans_by_user(self, user_id: str, active_only: bool = False) -> List[Loan]:
        """
        Retrieve loans for a specific user.
        
        Args:
            user_id: ID of the user
            active_only: If True, return only active loans
            
        Returns:
            List of Loan objects
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if active_only:
                    cursor.execute(
                        "SELECT * FROM loans WHERE user_id = ? AND is_returned = 0 ORDER BY date_borrowed DESC",
                        (user_id,)
                    )
                else:
                    cursor.execute(
                        "SELECT * FROM loans WHERE user_id = ? ORDER BY date_borrowed DESC",
                        (user_id,)
                    )
                
                rows = cursor.fetchall()
                return [self._row_to_loan(row) for row in rows]
                
        except sqlite3.Error as e:
            print(f"Error retrieving user loans: {e}")
            return []
    
    def get_overdue_loans(self) -> List[Loan]:
        """
        Retrieve all overdue loans.
        
        Returns:
            List of overdue Loan objects
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                current_time = datetime.now().isoformat()
                cursor.execute(
                    "SELECT * FROM loans WHERE is_returned = 0 AND date_due < ? ORDER BY date_due",
                    (current_time,)
                )
                rows = cursor.fetchall()
                
                return [self._row_to_loan(row) for row in rows]
                
        except sqlite3.Error as e:
            print(f"Error retrieving overdue loans: {e}")
            return []
    
    def _row_to_loan(self, row: sqlite3.Row) -> Loan:
        """Convert a database row to a Loan object."""
        # Calculate loan period
        date_borrowed = datetime.fromisoformat(row['date_borrowed'])
        date_due = datetime.fromisoformat(row['date_due'])
        loan_period = (date_due - date_borrowed).days
        
        # Create loan object
        loan = Loan(row['user_id'], row['item_id'], loan_period)
        
        # Override with saved data
        loan._loan_id = row['loan_id']
        loan._date_borrowed = date_borrowed
        loan._date_due = date_due
        loan._is_returned = bool(row['is_returned'])
        loan._fine_amount = row['fine_amount'] or 0.0
        loan._renewal_count = row['renewal_count'] or 0
        
        if row['date_returned']:
            loan._date_returned = datetime.fromisoformat(row['date_returned'])
        
        return loan
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_connection() 