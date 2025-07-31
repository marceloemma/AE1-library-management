"""
Abstract base classes for the Library Management System.

This module defines the abstract base classes that establish the contract
for library items and users, demonstrating encapsulation and abstraction principles.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class LibraryItem(ABC):
    """
    Abstract base class for all library items.
    
    All library items (books, magazines, DVDs) inherit from this class.
    Uses abstract methods to enforce implementation in subclasses.
    """
    
    # Static attribute to track total number of items created
    _total_items = 0
    
    def __init__(self, item_id: str, title: str):
        """Create a new library item."""
        if not item_id or not item_id.strip():
            raise ValueError("Item ID cannot be empty")
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
            
        self._item_id = item_id.strip()
        self._title = title.strip()
        self._is_available = True
        self._date_added = datetime.now()
        
        # keep track of how many items we've made
        LibraryItem._total_items += 1
    
    # Properties for encapsulation
    @property
    def item_id(self) -> str:
        """Get the item ID (read-only)."""
        return self._item_id
    
    @property
    def title(self) -> str:
        """Get the item title."""
        return self._title
    
    @title.setter
    def title(self, value: str):
        """Set the item title with validation."""
        if not value or not value.strip():
            raise ValueError("Title cannot be empty")
        self._title = value.strip()
    
    @property
    def is_available(self) -> bool:
        """Check if the item is available for borrowing."""
        return self._is_available
    
    @property
    def date_added(self) -> datetime:
        """Get the date when the item was added (read-only)."""
        return self._date_added
    
    @staticmethod
    def get_total_items() -> int:
        """Get the total number of library items created."""
        return LibraryItem._total_items
    
    @abstractmethod
    def check_out(self, user_id: str) -> bool:
        """
        Abstract method to check out the item to a user.
        
        Args:
            user_id: ID of the user checking out the item
            
        Returns:
            bool: True if checkout successful, False otherwise
        """
        pass
    
    @abstractmethod
    def check_in(self) -> bool:
        """
        Abstract method to check in the item.
        
        Returns:
            bool: True if check-in successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_item_type(self) -> str:
        """
        Abstract method to get the type of the item.
        
        Returns:
            str: The type of the library item
        """
        pass
    
    def __str__(self) -> str:
        """String representation of the library item."""
        status = "Available" if self._is_available else "Checked out"
        return f"{self.get_item_type()}: {self._title} (ID: {self._item_id}) - {status}"
    
    def __repr__(self) -> str:
        """Developer-friendly representation of the library item."""
        return f"{self.__class__.__name__}(item_id='{self._item_id}', title='{self._title}')"


class User(ABC):
    """
    Base class for library users (members and staff).
    
    Contains common user properties and enforces implementation 
    of role-specific methods in subclasses.
    """
    
    # Static attribute to track total number of users
    _total_users = 0
    
    def __init__(self, user_id: str, name: str, email: str):
        """Create a new user with basic info."""
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        if not self._is_valid_email(email):
            raise ValueError("Invalid email format")
            
        self._user_id = user_id.strip()
        self._name = name.strip()
        self._email = email
        self._registration_date = datetime.now()
        
        # keep count of users
        User._total_users += 1
    
    # Properties for encapsulation
    @property
    def user_id(self) -> str:
        """Get the user ID (read-only)."""
        return self._user_id
    
    @property
    def name(self) -> str:
        """Get the user name."""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Set the user name with validation."""
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        self._name = value.strip()
    
    @property
    def email(self) -> str:
        """Get the user email."""
        return self._email
    
    @email.setter
    def email(self, value: str):
        """Set the user email with validation."""
        if not self._is_valid_email(value):
            raise ValueError("Invalid email format")
        self._email = value
    
    @property
    def registration_date(self) -> datetime:
        """Get the user registration date (read-only)."""
        return self._registration_date
    
    @staticmethod
    def get_total_users() -> int:
        """Get the total number of users registered."""
        return User._total_users
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """
        Basic email validation.
        
        Args:
            email: Email address to validate
            
        Returns:
            bool: True if email format is valid, False otherwise
        """
        return "@" in email and "." in email.split("@")[-1]
    
    @abstractmethod
    def get_borrowing_limit(self) -> int:
        """
        Abstract method to get the borrowing limit for this user type.
        
        Returns:
            int: Maximum number of items this user can borrow
        """
        pass
    
    @abstractmethod
    def get_role(self) -> str:
        """
        Abstract method to get the role/type of the user.
        
        Returns:
            str: The role of the user ('Member', 'Staff')
        """
        pass
    
    @abstractmethod
    def can_borrow_item(self, item: LibraryItem) -> bool:
        """
        Abstract method to check if the user can borrow a specific item.
        
        Args:
            item: The library item to check
            
        Returns:
            bool: True if user can borrow the item, False otherwise
        """
        pass
    
    def __str__(self) -> str:
        """String representation of the user."""
        return f"{self.get_role()}: {self._name} (ID: {self._user_id})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation of the user."""
        return f"{self.__class__.__name__}(user_id='{self._user_id}', name='{self._name}', email='{self._email}')" 