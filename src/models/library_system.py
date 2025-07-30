"""
Main LibrarySystem class for coordinating all library operations.

This module contains the LibrarySystem class which serves as the central controller
for managing users, items, loans, and all business logic operations.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from .abstract_classes import LibraryItem, User
from .items import Book, Magazine, DVD
from .users import Member, Staff
from .loan import Loan


class LibrarySystem:
    """
    Central controller class for the library management system.
    
    Demonstrates:
    - Composition pattern (containing and managing other objects)
    - Business logic coordination
    - Error handling and validation
    - Statistical reporting and analytics
    """
    
    def __init__(self, name: str = "City Library"):
        """
        Initialise the library system.
        
        Args:
            name: Name of the library
        """
        self._name = name
        self._items: Dict[str, LibraryItem] = {}  # item_id -> LibraryItem
        self._users: Dict[str, User] = {}  # user_id -> User
        self._loans: Dict[str, Loan] = {}  # loan_id -> Loan
        self._active_loans: Dict[str, List[str]] = {}  # user_id -> [loan_ids]
        self._system_startup_time = datetime.now()
    
    # Properties
    @property
    def name(self) -> str:
        """Get the library name."""
        return self._name
    
    @property
    def total_items(self) -> int:
        """Get the total number of items in the library."""
        return len(self._items)
    
    @property
    def total_users(self) -> int:
        """Get the total number of registered users."""
        return len(self._users)
    
    @property
    def total_loans(self) -> int:
        """Get the total number of loans (active and historical)."""
        return len(self._loans)
    
    @property
    def active_loans_count(self) -> int:
        """Get the number of currently active loans."""
        return sum(1 for loan in self._loans.values() if not loan.is_returned)
    
    # User Management Methods
    def register_user(self, user: User) -> bool:
        """
        Register a new user in the system.
        
        Args:
            user: User object to register
            
        Returns:
            bool: True if registration successful, False if user already exists
        """
        if user.user_id in self._users:
            return False
        
        self._users[user.user_id] = user
        self._active_loans[user.user_id] = []
        return True
    
    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        return self._users.get(user_id)
    
    def remove_user(self, user_id: str) -> bool:
        """
        Remove a user from the system.
        
        Args:
            user_id: ID of the user to remove
            
        Returns:
            bool: True if removal successful, False if user has active loans or not found
        """
        if user_id not in self._users:
            return False
        
        # Check if user has active loans
        if self._active_loans.get(user_id) and len(self._active_loans[user_id]) > 0:
            return False
        
        del self._users[user_id]
        if user_id in self._active_loans:
            del self._active_loans[user_id]
        return True
    
    def get_all_users(self) -> List[User]:
        """
        Get all registered users.
        
        Returns:
            List of all User objects
        """
        return list(self._users.values())
    
    def get_users_by_role(self, role: str) -> List[User]:
        """
        Get all users with a specific role.
        
        Args:
            role: Role to filter by ('Member' or 'Staff')
            
        Returns:
            List of User objects with the specified role
        """
        return [user for user in self._users.values() if user.get_role() == role]
    
    # Item Management Methods
    def add_item(self, item: LibraryItem) -> bool:
        """
        Add a new item to the library.
        
        Args:
            item: LibraryItem object to add
            
        Returns:
            bool: True if addition successful, False if item already exists
        """
        if item.item_id in self._items:
            return False
        
        self._items[item.item_id] = item
        return True
    
    def get_item(self, item_id: str) -> Optional[LibraryItem]:
        """
        Get an item by its ID.
        
        Args:
            item_id: ID of the item to retrieve
            
        Returns:
            LibraryItem object if found, None otherwise
        """
        return self._items.get(item_id)
    
    def remove_item(self, item_id: str) -> bool:
        """
        Remove an item from the library.
        
        Args:
            item_id: ID of the item to remove
            
        Returns:
            bool: True if removal successful, False if item is currently borrowed or not found
        """
        if item_id not in self._items:
            return False
        
        item = self._items[item_id]
        if not item.is_available:
            return False  # Cannot remove borrowed items
        
        del self._items[item_id]
        return True
    
    def get_all_items(self) -> List[LibraryItem]:
        """
        Get all items in the library.
        
        Returns:
            List of all LibraryItem objects
        """
        return list(self._items.values())
    
    def get_available_items(self) -> List[LibraryItem]:
        """
        Get all available items.
        
        Returns:
            List of available LibraryItem objects
        """
        return [item for item in self._items.values() if item.is_available]
    
    def get_items_by_type(self, item_type: str) -> List[LibraryItem]:
        """
        Get all items of a specific type.
        
        Args:
            item_type: Type to filter by ('Book', 'Magazine', 'DVD')
            
        Returns:
            List of LibraryItem objects of the specified type
        """
        return [item for item in self._items.values() if item.get_item_type() == item_type]
    
    def search_items(self, query: str) -> List[LibraryItem]:
        """
        Search for items by title.
        
        Args:
            query: Search query (partial title match, case-insensitive)
            
        Returns:
            List of LibraryItem objects matching the search
        """
        query_lower = query.lower()
        return [item for item in self._items.values() 
                if query_lower in item.title.lower()]
    
    # Loan Management Methods
    def check_out_item(self, user_id: str, item_id: str) -> Tuple[bool, str]:
        """
        Check out an item to a user.
        
        Args:
            user_id: ID of the user checking out the item
            item_id: ID of the item to check out
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Validate user
        user = self.get_user(user_id)
        if not user:
            return False, "User not found"
        
        # Validate item
        item = self.get_item(item_id)
        if not item:
            return False, "Item not found"
        
        # Check if user can borrow this item
        if not user.can_borrow_item(item):
            return False, "User cannot borrow this item (check limits, fines, or membership status)"
        
        # Check if item is available
        if not item.is_available:
            return False, "Item is not available"
        
        # Create loan
        loan_period = item.get_loan_period() if hasattr(item, 'get_loan_period') else 21
        loan = Loan(user_id, item_id, loan_period)
        
        # Check out the item
        if item.check_out(user_id):
            self._loans[loan.loan_id] = loan
            self._active_loans[user_id].append(loan.loan_id)
            
            # Update user's borrowed items if applicable
            if hasattr(user, 'borrow_item'):
                user.borrow_item(item_id)
            
            return True, f"Item checked out successfully. Due date: {loan.date_due.strftime('%Y-%m-%d')}"
        else:
            return False, "Failed to check out item"
    
    def check_in_item(self, user_id: str, item_id: str) -> Tuple[bool, str, float]:
        """
        Check in an item from a user.
        
        Args:
            user_id: ID of the user returning the item
            item_id: ID of the item to check in
            
        Returns:
            Tuple of (success: bool, message: str, fine_amount: float)
        """
        # Find the active loan
        active_loan = None
        for loan_id in self._active_loans.get(user_id, []):
            loan = self._loans.get(loan_id)
            if loan and loan.item_id == item_id and not loan.is_returned:
                active_loan = loan
                break
        
        if not active_loan:
            return False, "No active loan found for this item and user", 0.0
        
        # Get the item
        item = self.get_item(item_id)
        if not item:
            return False, "Item not found", 0.0
        
        # Return the item
        fine_amount = active_loan.return_item()
        
        if item.check_in():
            # Remove from active loans
            self._active_loans[user_id].remove(active_loan.loan_id)
            
            # Update user's borrowed items if applicable
            user = self.get_user(user_id)
            if user and hasattr(user, 'return_item'):
                user.return_item(item_id)
            
            # Add loan to user's history and apply fine if applicable
            if hasattr(user, 'add_loan_to_history'):
                user.add_loan_to_history(active_loan.loan_id)
            
            if fine_amount > 0 and hasattr(user, 'add_fine'):
                user.add_fine(fine_amount)
            
            message = f"Item returned successfully."
            if fine_amount > 0:
                message += f" Fine owed: ${fine_amount:.2f}"
            
            return True, message, fine_amount
        else:
            return False, "Failed to check in item", 0.0
    
    def renew_loan(self, user_id: str, item_id: str) -> Tuple[bool, str]:
        """
        Renew a loan for additional time.
        
        Args:
            user_id: ID of the user renewing the loan
            item_id: ID of the item to renew
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Find the active loan
        active_loan = None
        for loan_id in self._active_loans.get(user_id, []):
            loan = self._loans.get(loan_id)
            if loan and loan.item_id == item_id and not loan.is_returned:
                active_loan = loan
                break
        
        if not active_loan:
            return False, "No active loan found for this item and user"
        
        if active_loan.renew_loan():
            return True, f"Loan renewed successfully. New due date: {active_loan.date_due.strftime('%Y-%m-%d')}"
        else:
            return False, "Cannot renew loan (maximum renewals reached or item is overdue)"
    
    def get_user_loans(self, user_id: str, active_only: bool = True) -> List[Loan]:
        """
        Get loans for a specific user.
        
        Args:
            user_id: ID of the user
            active_only: If True, return only active loans; if False, return all loans
            
        Returns:
            List of Loan objects for the user
        """
        if active_only:
            loan_ids = self._active_loans.get(user_id, [])
            return [self._loans[loan_id] for loan_id in loan_ids if loan_id in self._loans]
        else:
            return [loan for loan in self._loans.values() if loan.user_id == user_id]
    
    def get_overdue_loans(self) -> List[Loan]:
        """
        Get all overdue loans.
        
        Returns:
            List of overdue Loan objects
        """
        return [loan for loan in self._loans.values() 
                if not loan.is_returned and loan.is_overdue()]
    
    # Reporting and Analytics Methods
    def get_system_statistics(self) -> Dict[str, Union[int, float, str]]:
        """
        Get comprehensive system statistics.
        
        Returns:
            Dictionary containing various system statistics
        """
        overdue_loans = self.get_overdue_loans()
        members = self.get_users_by_role('Member')
        staff = self.get_users_by_role('Staff')
        
        return {
            'library_name': self._name,
            'total_items': self.total_items,
            'available_items': len(self.get_available_items()),
            'total_users': self.total_users,
            'total_members': len(members),
            'total_staff': len(staff),
            'total_loans': self.total_loans,
            'active_loans': self.active_loans_count,
            'overdue_loans': len(overdue_loans),
            'total_fines_owed': sum(loan.fine_amount for loan in overdue_loans),
            'books_count': len(self.get_items_by_type('Book')),
            'magazines_count': len(self.get_items_by_type('Magazine')),
            'dvds_count': len(self.get_items_by_type('DVD')),
            'system_uptime_days': (datetime.now() - self._system_startup_time).days
        }
    
    def get_popular_items(self, limit: int = 10) -> List[Tuple[LibraryItem, int]]:
        """
        Get the most popular items based on loan count.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List of tuples (item, loan_count) sorted by popularity
        """
        item_loan_counts = {}
        
        for loan in self._loans.values():
            item_id = loan.item_id
            if item_id in self._items:
                item_loan_counts[item_id] = item_loan_counts.get(item_id, 0) + 1
        
        # Sort by loan count and return top items
        sorted_items = sorted(item_loan_counts.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        for item_id, count in sorted_items[:limit]:
            item = self._items.get(item_id)
            if item:
                result.append((item, count))
        
        return result
    
    def get_member_activity_report(self, user_id: str) -> Dict[str, Union[int, float, List]]:
        """
        Get a detailed activity report for a specific member.
        
        Args:
            user_id: ID of the member
            
        Returns:
            Dictionary containing member activity statistics
        """
        user = self.get_user(user_id)
        if not user:
            return {}
        
        all_loans = self.get_user_loans(user_id, active_only=False)
        active_loans = self.get_user_loans(user_id, active_only=True)
        overdue_loans = [loan for loan in active_loans if loan.is_overdue()]
        
        total_fines = 0
        if hasattr(user, 'fines_owed'):
            total_fines = user.fines_owed
        
        return {
            'user_name': user.name,
            'user_role': user.get_role(),
            'total_loans': len(all_loans),
            'active_loans': len(active_loans),
            'overdue_loans': len(overdue_loans),
            'total_fines_owed': total_fines,
            'borrowing_limit': user.get_borrowing_limit(),
            'loan_history': [loan.to_dict() for loan in all_loans[-10:]]  # Last 10 loans
        }
    
    def validate_system_integrity(self) -> List[str]:
        """
        Validate the integrity of the system data.
        
        Returns:
            List of error messages (empty if no issues found)
        """
        errors = []
        
        # Check for orphaned loans
        for loan in self._loans.values():
            if loan.user_id not in self._users:
                errors.append(f"Loan {loan.loan_id} references non-existent user {loan.user_id}")
            if loan.item_id not in self._items:
                errors.append(f"Loan {loan.loan_id} references non-existent item {loan.item_id}")
        
        # Check for inconsistent item availability
        for item in self._items.values():
            active_loans = [loan for loan in self._loans.values() 
                          if loan.item_id == item.item_id and not loan.is_returned]
            
            if len(active_loans) > 1:
                errors.append(f"Item {item.item_id} has multiple active loans")
            elif len(active_loans) == 1 and item.is_available:
                errors.append(f"Item {item.item_id} is marked available but has an active loan")
            elif len(active_loans) == 0 and not item.is_available:
                errors.append(f"Item {item.item_id} is marked unavailable but has no active loan")
        
        return errors
    
    def __str__(self) -> str:
        """String representation of the library system."""
        stats = self.get_system_statistics()
        return (f"Library System: {self._name}\n"
                f"Items: {stats['total_items']} ({stats['available_items']} available)\n"
                f"Users: {stats['total_users']} ({stats['total_members']} members, {stats['total_staff']} staff)\n"
                f"Loans: {stats['active_loans']} active, {stats['overdue_loans']} overdue")
    
    def __repr__(self) -> str:
        """Developer-friendly representation of the library system."""
        return f"LibrarySystem(name='{self._name}', items={len(self._items)}, users={len(self._users)})" 