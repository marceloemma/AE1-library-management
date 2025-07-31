"""
Concrete implementations of LibraryItem subclasses.

This module contains the specific types of library items that inherit from
the LibraryItem abstract base class, demonstrating inheritance and polymorphism.
"""

from datetime import datetime, timedelta
from typing import Optional
from .abstract_classes import LibraryItem


class Book(LibraryItem):
    """Book with author, ISBN, and page count."""
    
    # Static attribute specific to books
    _total_books = 0
    
    def __init__(self, item_id: str, title: str, author: str, isbn: str, pages: int = 0):
        """Create a new book."""
        super().__init__(item_id, title)
        self._author = author
        self._isbn = isbn
        self._pages = pages
        
        # count books created
        Book._total_books += 1
    
    # Properties for book-specific attributes
    @property
    def author(self) -> str:
        """Get the author."""
        return self._author
    
    @property
    def isbn(self) -> str:
        """Get the ISBN."""
        return self._isbn
    
    @property
    def pages(self) -> int:
        """Get the page count."""
        return self._pages
    
    @staticmethod
    def get_total_books() -> int:
        """Get total number of books."""
        return Book._total_books
    
    # Override abstract methods
    def check_out(self, user_id: str) -> bool:
        """Check out this book to a user."""
        if not self._is_available:
            return False
        self._is_available = False
        return True
    
    def check_in(self) -> bool:
        """Return this book."""
        if self._is_available:
            return False  # wasn't checked out
        self._is_available = True
        return True
    
    def get_item_type(self) -> str:
        """Returns 'Book'."""
        return "Book"
    
    def get_loan_period(self):
        """Books can be borrowed for 21 days."""
        return 21
    
    def to_dict(self) -> dict:
        """Convert book to dictionary for database storage."""
        return {
            'item_id': self._item_id,
            'title': self._title,
            'type': 'Book',
            'author': self._author,
            'isbn': self._isbn,
            'pages': self._pages,
            'is_available': self._is_available,
            'date_added': self._date_added.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create book from dictionary data."""
        book = cls(
            item_id=data['item_id'],
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            pages=data.get('pages', 0)
        )
        book._is_available = data.get('is_available', True)
        if 'date_added' in data:
            book._date_added = datetime.fromisoformat(data['date_added'])
        return book
    
    def __str__(self) -> str:
        """String representation of the book."""
        status = "Available" if self._is_available else "Checked out"
        return f"Book: '{self._title}' by {self._author} - {status}"


class Magazine(LibraryItem):
    """Magazine with publisher and issue info. Shorter loan period than books."""
    
    # Static attribute specific to magazines
    _total_magazines = 0
    
    def __init__(self, item_id: str, title: str, issue_number: str, publisher: str, 
                 publication_date: Optional[datetime] = None):
        """Create a new magazine."""
        super().__init__(item_id, title)
        self._issue_number = issue_number
        self._publisher = publisher
        self._publication_date = publication_date or datetime.now()
        
        Magazine._total_magazines += 1
    
    # Properties
    @property
    def issue_number(self) -> str:
        """Get the issue number."""
        return self._issue_number
    
    @property
    def publisher(self) -> str:
        """Get the publisher."""
        return self._publisher
    
    @property
    def publication_date(self) -> datetime:
        """Get the publication date."""
        return self._publication_date
    
    @staticmethod
    def get_total_magazines() -> int:
        """Get total number of magazines."""
        return Magazine._total_magazines
    
    # Override abstract methods
    def check_out(self, user_id: str) -> bool:
        """Check out this magazine."""
        if not self._is_available:
            return False
        self._is_available = False
        return True
    
    def check_in(self) -> bool:
        """Return this magazine."""
        if self._is_available:
            return False
        self._is_available = True
        return True
    
    def get_item_type(self) -> str:
        """Returns 'Magazine'."""
        return "Magazine"
    
    def get_loan_period(self):
        """Magazines have a shorter 7-day loan period."""
        return 7  # shorter period for magazines
    
    def to_dict(self) -> dict:
        """Convert to dict for storage."""
        return {
            'item_id': self._item_id,
            'title': self._title,
            'type': 'Magazine',
            'issue_number': self._issue_number,
            'publisher': self._publisher,
            'publication_date': self._publication_date.isoformat(),
            'is_available': self._is_available,
            'date_added': self._date_added.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create magazine from dict."""
        pub_date = None
        if 'publication_date' in data:
            pub_date = datetime.fromisoformat(data['publication_date'])
        
        magazine = cls(
            item_id=data['item_id'],
            title=data['title'],
            issue_number=data['issue_number'],
            publisher=data['publisher'],
            publication_date=pub_date
        )
        magazine._is_available = data.get('is_available', True)
        if 'date_added' in data:
            magazine._date_added = datetime.fromisoformat(data['date_added'])
        return magazine
    
    def __str__(self) -> str:
        """String representation of the magazine."""
        status = "Available" if self._is_available else "Checked out"
        return f"Magazine: '{self._title}' Issue {self._issue_number} by {self._publisher} - {status}"


class DVD(LibraryItem):
    """DVD with runtime, genre, director and rating info."""
    
    # Static attribute specific to DVDs
    _total_dvds = 0
    
    def __init__(self, item_id: str, title: str, duration: int, genre: str, 
                 director: Optional[str] = None, rating: Optional[str] = None):
        """Create a new DVD."""
        super().__init__(item_id, title)
        self._duration = max(0, duration)  # can't have negative runtime
        self._genre = genre
        self._director = director or "Unknown"
        self._rating = rating or "NR"  # Not Rated
        
        DVD._total_dvds += 1
    
    # Properties
    @property
    def duration(self) -> int:
        """Get the duration in minutes."""
        return self._duration
    
    @property
    def genre(self) -> str:
        """Get the genre."""
        return self._genre
    
    @property
    def director(self) -> str:
        """Get the director."""
        return self._director
    
    @property
    def rating(self) -> str:
        """Get the rating."""
        return self._rating
    
    @staticmethod
    def get_total_dvds() -> int:
        """Get total DVDs."""
        return DVD._total_dvds
    
    # Override abstract methods
    def check_out(self, user_id: str) -> bool:
        """Check out this DVD."""
        if not self._is_available:
            return False
        self._is_available = False
        return True
    
    def check_in(self) -> bool:
        """Return this DVD."""
        if self._is_available:
            return False
        self._is_available = True
        return True
    
    def get_item_type(self) -> str:
        """Returns 'DVD'."""
        return "DVD"
    
    def get_loan_period(self):
        """DVDs can be borrowed for 2 weeks."""
        return 14  # 2 weeks
    
    def to_dict(self) -> dict:
        """Convert to dict."""
        return {
            'item_id': self._item_id,
            'title': self._title,
            'type': 'DVD',
            'duration': self._duration,
            'genre': self._genre,
            'director': self._director,
            'rating': self._rating,
            'is_available': self._is_available,
            'date_added': self._date_added.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create DVD from dict."""
        dvd = cls(
            item_id=data['item_id'],
            title=data['title'],
            duration=data.get('duration', 0),
            genre=data.get('genre', 'Unknown'),
            director=data.get('director'),
            rating=data.get('rating')
        )
        dvd._is_available = data.get('is_available', True)
        if 'date_added' in data:
            dvd._date_added = datetime.fromisoformat(data['date_added'])
        return dvd
    
    def __str__(self) -> str:
        """String representation."""
        status = "Available" if self._is_available else "Checked out"
        return f"DVD: '{self._title}' ({self._duration}min, {self._genre}) - {status}" 