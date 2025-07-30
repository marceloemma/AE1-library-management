"""
Concrete implementations of LibraryItem subclasses.

This module contains the specific types of library items that inherit from
the LibraryItem abstract base class, demonstrating inheritance and polymorphism.
"""

from datetime import datetime, timedelta
from typing import Optional
from .abstract_classes import LibraryItem


class Book(LibraryItem):
    """
    Book class inheriting from LibraryItem.
    
    Demonstrates:
    - Inheritance from abstract base class
    - Method overriding (polymorphism)
    - Additional specific attributes for books
    """
    
    # Static attribute specific to books
    _total_books = 0
    
    def __init__(self, item_id: str, title: str, author: str, isbn: str, pages: int = 0):
        """
        Initialise a book.
        
        Args:
            item_id: Unique identifier for the book
            title: Title of the book
            author: Author of the book
            isbn: ISBN number of the book
            pages: Number of pages (optional)
        """
        super().__init__(item_id, title)  # Call parent constructor
        self._author = author
        self._isbn = isbn
        self._pages = pages
        
        # Increment book-specific counter
        Book._total_books += 1
    
    # Properties for book-specific attributes
    @property
    def author(self) -> str:
        """Get the book author."""
        return self._author
    
    @author.setter
    def author(self, value: str):
        """Set the book author with validation."""
        if not value or not value.strip():
            raise ValueError("Author cannot be empty")
        self._author = value.strip()
    
    @property
    def isbn(self) -> str:
        """Get the book ISBN."""
        return self._isbn
    
    @isbn.setter
    def isbn(self, value: str):
        """Set the book ISBN with validation."""
        if not value or not value.strip():
            raise ValueError("ISBN cannot be empty")
        self._isbn = value.strip()
    
    @property
    def pages(self) -> int:
        """Get the number of pages."""
        return self._pages
    
    @pages.setter
    def pages(self, value: int):
        """Set the number of pages with validation."""
        if value < 0:
            raise ValueError("Pages cannot be negative")
        self._pages = value
    
    @staticmethod
    def get_total_books() -> int:
        """Get the total number of books created."""
        return Book._total_books
    
    # Override abstract methods (polymorphism)
    def check_out(self, user_id: str) -> bool:
        """
        Check out the book to a user.
        
        Args:
            user_id: ID of the user checking out the book
            
        Returns:
            bool: True if checkout successful, False otherwise
        """
        if not self._is_available:
            return False
        
        self._is_available = False
        self._current_borrower = user_id
        self._checkout_date = datetime.now()
        return True
    
    def check_in(self) -> bool:
        """
        Check in the book.
        
        Returns:
            bool: True if check-in successful, False otherwise
        """
        if self._is_available:
            return False
        
        self._is_available = True
        self._current_borrower = None
        self._checkout_date = None
        return True
    
    def get_item_type(self) -> str:
        """
        Get the type of the item.
        
        Returns:
            str: "Book"
        """
        return "Book"
    
    def get_loan_period(self) -> int:
        """
        Get the loan period for books in days.
        
        Returns:
            int: Number of days for book loan (21 days for books)
        """
        return 21
    
    def __str__(self) -> str:
        """String representation of the book."""
        status = "Available" if self._is_available else "Checked out"
        return f"Book: '{self._title}' by {self._author} (ISBN: {self._isbn}) - {status}"


class Magazine(LibraryItem):
    """
    Magazine class inheriting from LibraryItem.
    
    Demonstrates:
    - Inheritance from abstract base class
    - Method overriding with different behavior
    - Magazine-specific attributes
    """
    
    # Static attribute specific to magazines
    _total_magazines = 0
    
    def __init__(self, item_id: str, title: str, issue_number: str, publisher: str, 
                 publication_date: Optional[datetime] = None):
        """
        Initialise a magazine.
        
        Args:
            item_id: Unique identifier for the magazine
            title: Title of the magazine
            issue_number: Issue number or identifier
            publisher: Publisher of the magazine
            publication_date: Date of publication (optional)
        """
        super().__init__(item_id, title)
        self._issue_number = issue_number
        self._publisher = publisher
        self._publication_date = publication_date or datetime.now()
        
        # Increment magazine-specific counter
        Magazine._total_magazines += 1
    
    # Properties for magazine-specific attributes
    @property
    def issue_number(self) -> str:
        """Get the magazine issue number."""
        return self._issue_number
    
    @issue_number.setter
    def issue_number(self, value: str):
        """Set the magazine issue number with validation."""
        if not value or not value.strip():
            raise ValueError("Issue number cannot be empty")
        self._issue_number = value.strip()
    
    @property
    def publisher(self) -> str:
        """Get the magazine publisher."""
        return self._publisher
    
    @publisher.setter
    def publisher(self, value: str):
        """Set the magazine publisher with validation."""
        if not value or not value.strip():
            raise ValueError("Publisher cannot be empty")
        self._publisher = value.strip()
    
    @property
    def publication_date(self) -> datetime:
        """Get the magazine publication date."""
        return self._publication_date
    
    @staticmethod
    def get_total_magazines() -> int:
        """Get the total number of magazines created."""
        return Magazine._total_magazines
    
    # Override abstract methods (polymorphism with different behavior)
    def check_out(self, user_id: str) -> bool:
        """
        Check out the magazine to a user.
        Magazines have shorter loan periods.
        
        Args:
            user_id: ID of the user checking out the magazine
            
        Returns:
            bool: True if checkout successful, False otherwise
        """
        if not self._is_available:
            return False
        
        self._is_available = False
        self._current_borrower = user_id
        self._checkout_date = datetime.now()
        return True
    
    def check_in(self) -> bool:
        """
        Check in the magazine.
        
        Returns:
            bool: True if check-in successful, False otherwise
        """
        if self._is_available:
            return False
        
        self._is_available = True
        self._current_borrower = None
        self._checkout_date = None
        return True
    
    def get_item_type(self) -> str:
        """
        Get the type of the item.
        
        Returns:
            str: "Magazine"
        """
        return "Magazine"
    
    def get_loan_period(self) -> int:
        """
        Get the loan period for magazines in days.
        
        Returns:
            int: Number of days for magazine loan (7 days for magazines)
        """
        return 7
    
    def __str__(self) -> str:
        """String representation of the magazine."""
        status = "Available" if self._is_available else "Checked out"
        return f"Magazine: '{self._title}' Issue {self._issue_number} by {self._publisher} - {status}"


class DVD(LibraryItem):
    """
    DVD class inheriting from LibraryItem.
    
    Demonstrates:
    - Inheritance from abstract base class
    - Method overriding with DVD-specific logic
    - Additional validation for DVD-specific attributes
    """
    
    # Static attribute specific to DVDs
    _total_dvds = 0
    
    def __init__(self, item_id: str, title: str, duration: int, genre: str, 
                 director: Optional[str] = None, rating: Optional[str] = None):
        """
        Initialise a DVD.
        
        Args:
            item_id: Unique identifier for the DVD
            title: Title of the DVD
            duration: Duration in minutes
            genre: Genre of the DVD
            director: Director of the DVD (optional)
            rating: Age rating of the DVD (optional)
        """
        super().__init__(item_id, title)
        self._duration = duration
        self._genre = genre
        self._director = director
        self._rating = rating
        
        # Increment DVD-specific counter
        DVD._total_dvds += 1
    
    # Properties for DVD-specific attributes
    @property
    def duration(self) -> int:
        """Get the DVD duration in minutes."""
        return self._duration
    
    @duration.setter
    def duration(self, value: int):
        """Set the DVD duration with validation."""
        if value <= 0:
            raise ValueError("Duration must be positive")
        self._duration = value
    
    @property
    def genre(self) -> str:
        """Get the DVD genre."""
        return self._genre
    
    @genre.setter
    def genre(self, value: str):
        """Set the DVD genre with validation."""
        if not value or not value.strip():
            raise ValueError("Genre cannot be empty")
        self._genre = value.strip()
    
    @property
    def director(self) -> Optional[str]:
        """Get the DVD director."""
        return self._director
    
    @director.setter
    def director(self, value: Optional[str]):
        """Set the DVD director."""
        self._director = value.strip() if value else None
    
    @property
    def rating(self) -> Optional[str]:
        """Get the DVD rating."""
        return self._rating
    
    @rating.setter
    def rating(self, value: Optional[str]):
        """Set the DVD rating with validation."""
        valid_ratings = ["G", "PG", "PG-13", "R", "NC-17", "NR"]
        if value and value not in valid_ratings:
            raise ValueError(f"Rating must be one of: {', '.join(valid_ratings)}")
        self._rating = value
    
    @staticmethod
    def get_total_dvds() -> int:
        """Get the total number of DVDs created."""
        return DVD._total_dvds
    
    # Override abstract methods (polymorphism with DVD-specific behavior)
    def check_out(self, user_id: str) -> bool:
        """
        Check out the DVD to a user.
        DVDs may have age restrictions.
        
        Args:
            user_id: ID of the user checking out the DVD
            
        Returns:
            bool: True if checkout successful, False otherwise
        """
        if not self._is_available:
            return False
        
        # Note: In a real system, we'd check user age against rating here
        self._is_available = False
        self._current_borrower = user_id
        self._checkout_date = datetime.now()
        return True
    
    def check_in(self) -> bool:
        """
        Check in the DVD.
        
        Returns:
            bool: True if check-in successful, False otherwise
        """
        if self._is_available:
            return False
        
        self._is_available = True
        self._current_borrower = None
        self._checkout_date = None
        return True
    
    def get_item_type(self) -> str:
        """
        Get the type of the item.
        
        Returns:
            str: "DVD"
        """
        return "DVD"
    
    def get_loan_period(self) -> int:
        """
        Get the loan period for DVDs in days.
        
        Returns:
            int: Number of days for DVD loan (14 days for DVDs)
        """
        return 14
    
    def get_formatted_duration(self) -> str:
        """
        Get the duration formatted as hours and minutes.
        
        Returns:
            str: Duration in "Xh Ym" format
        """
        hours = self._duration // 60
        minutes = self._duration % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def __str__(self) -> str:
        """String representation of the DVD."""
        status = "Available" if self._is_available else "Checked out"
        director_info = f" directed by {self._director}" if self._director else ""
        return f"DVD: '{self._title}'{director_info} ({self.get_formatted_duration()}, {self._genre}) - {status}" 