"""
Loan class for tracking library item borrowing transactions.

This module contains the Loan class which represents a borrowing transaction
between a user and a library item, including due dates and return tracking.
"""

from datetime import datetime, timedelta
from typing import Optional
import uuid


class Loan:
    """
    Tracks when a user borrows a library item.
    
    Handles due dates, renewals, and overdue fines.
    """
    
    # Static attributes for loan management
    _daily_fine_rate = 0.50  # $0.50 per day late
    _total_loans = 0
    
    def __init__(self, user_id: str, item_id: str, loan_period_days: int = 21):
        """Create a new loan record."""
        self._loan_id = str(uuid.uuid4())  # unique ID for this loan
        self._user_id = user_id
        self._item_id = item_id
        self._date_borrowed = datetime.now()
        self._date_due = self._date_borrowed + timedelta(days=loan_period_days)
        self._date_returned: Optional[datetime] = None
        self._is_returned = False
        self._fine_amount = 0.0
        self._renewal_count = 0
        self._max_renewals = 2  # can only renew twice
        
        # track total loans
        Loan._total_loans += 1
    
    # Properties for encapsulation
    @property
    def loan_id(self) -> str:
        """Get loan ID."""
        return self._loan_id
    
    @property
    def user_id(self) -> str:
        """Get user ID."""
        return self._user_id
    
    @property
    def item_id(self) -> str:
        """Get item ID."""
        return self._item_id
    
    @property
    def date_borrowed(self) -> datetime:
        """Get the date when the item was borrowed (read-only)."""
        return self._date_borrowed
    
    @property
    def date_due(self) -> datetime:
        """Get the due date for the loan."""
        return self._date_due
    
    @property
    def date_returned(self) -> Optional[datetime]:
        """Get the date when the item was returned (read-only)."""
        return self._date_returned
    
    @property
    def is_returned(self) -> bool:
        """Check if the item has been returned (read-only)."""
        return self._is_returned
    
    @property
    def fine_amount(self) -> float:
        """Get the current fine amount."""
        if not self._is_returned:
            self._calculate_current_fine()
        return self._fine_amount
    
    @property
    def renewal_count(self) -> int:
        """Get the number of times this loan has been renewed."""
        return self._renewal_count
    
    @property
    def max_renewals(self) -> int:
        """Get the maximum number of renewals allowed."""
        return self._max_renewals
    
    @staticmethod
    def get_total_loans() -> int:
        """Get the total number of loans created."""
        return Loan._total_loans
    
    @staticmethod
    def get_daily_fine_rate() -> float:
        """Get the daily fine rate."""
        return Loan._daily_fine_rate
    
    @staticmethod
    def set_daily_fine_rate(rate: float) -> None:
        """
        Set the daily fine rate.
        
        Args:
            rate: New daily fine rate
            
        Raises:
            ValueError: If rate is negative
        """
        if rate < 0:
            raise ValueError("Fine rate cannot be negative")
        Loan._daily_fine_rate = rate
    
    def is_overdue(self) -> bool:
        """
        Check if the loan is currently overdue.
        
        Returns:
            bool: True if the loan is overdue and not returned, False otherwise
        """
        if self._is_returned:
            return False
        return datetime.now() > self._date_due
    
    def days_overdue(self) -> int:
        """
        Calculate the number of days the loan is overdue.
        
        Returns:
            int: Number of days overdue (0 if not overdue or returned)
        """
        if self._is_returned or not self.is_overdue():
            return 0
        
        return (datetime.now() - self._date_due).days
    
    def _calculate_current_fine(self) -> None:
        """Calculate the current fine amount for an overdue loan."""
        if self.is_overdue():
            days_late = self.days_overdue()
            self._fine_amount = days_late * self._daily_fine_rate
        else:
            self._fine_amount = 0.0
    
    def return_item(self, return_date: Optional[datetime] = None) -> float:
        """
        Return the borrowed item and calculate final fine.
        
        Args:
            return_date: Date of return (defaults to current time)
            
        Returns:
            float: Final fine amount owed
            
        Raises:
            ValueError: If item is already returned
        """
        if self._is_returned:
            raise ValueError("Item has already been returned")
        
        self._date_returned = return_date or datetime.now()
        self._is_returned = True
        
        # Calculate final fine if returned late
        if self._date_returned > self._date_due:
            days_late = (self._date_returned - self._date_due).days
            self._fine_amount = days_late * self._daily_fine_rate
        else:
            self._fine_amount = 0.0
        
        return self._fine_amount
    
    def renew_loan(self, additional_days: int = 21) -> bool:
        """
        Renew the loan for additional days.
        
        Args:
            additional_days: Number of additional days to extend the loan
            
        Returns:
            bool: True if renewal was successful, False otherwise
        """
        if self._is_returned:
            return False
        
        if self._renewal_count >= self._max_renewals:
            return False
        
        if self.is_overdue():
            return False  # Cannot renew overdue items
        
        # Extend the due date
        self._date_due += timedelta(days=additional_days)
        self._renewal_count += 1
        
        return True
    
    def can_renew(self) -> bool:
        """
        Check if the loan can be renewed.
        
        Returns:
            bool: True if the loan can be renewed, False otherwise
        """
        if self._is_returned:
            return False
        
        if self._renewal_count >= self._max_renewals:
            return False
        
        if self.is_overdue():
            return False
        
        return True
    
    def get_loan_duration(self) -> int:
        """
        Get the total duration of the loan in days.
        
        Returns:
            int: Number of days the item has been/was borrowed
        """
        end_date = self._date_returned if self._is_returned else datetime.now()
        return (end_date - self._date_borrowed).days
    
    def get_status(self) -> str:
        """
        Get the current status of the loan.
        
        Returns:
            str: Status description (Active, Overdue, Returned, etc.)
        """
        if self._is_returned:
            if self._fine_amount > 0:
                return f"Returned Late (Fine: ${self._fine_amount:.2f})"
            else:
                return "Returned On Time"
        elif self.is_overdue():
            return f"Overdue ({self.days_overdue()} days)"
        else:
            days_remaining = (self._date_due - datetime.now()).days
            return f"Active ({days_remaining} days remaining)"
    
    def to_dict(self) -> dict:
        """
        Convert the loan to a dictionary representation.
        
        Returns:
            dict: Dictionary containing loan details
        """
        return {
            'loan_id': self._loan_id,
            'user_id': self._user_id,
            'item_id': self._item_id,
            'date_borrowed': self._date_borrowed.isoformat(),
            'date_due': self._date_due.isoformat(),
            'date_returned': self._date_returned.isoformat() if self._date_returned else None,
            'is_returned': self._is_returned,
            'fine_amount': self._fine_amount,
            'renewal_count': self._renewal_count,
            'status': self.get_status()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Loan':
        """
        Create a Loan instance from a dictionary.
        
        Args:
            data: Dictionary containing loan data
            
        Returns:
            Loan: New Loan instance
        """
        # Calculate loan period from borrowed and due dates
        date_borrowed = datetime.fromisoformat(data['date_borrowed'])
        date_due = datetime.fromisoformat(data['date_due'])
        loan_period = (date_due - date_borrowed).days
        
        # Create loan instance
        loan = cls(data['user_id'], data['item_id'], loan_period)
        
        # Override the generated values with saved data
        loan._loan_id = data['loan_id']
        loan._date_borrowed = date_borrowed
        loan._date_due = date_due
        loan._is_returned = data['is_returned']
        loan._fine_amount = data['fine_amount']
        loan._renewal_count = data['renewal_count']
        
        if data['date_returned']:
            loan._date_returned = datetime.fromisoformat(data['date_returned'])
        
        return loan
    
    def __str__(self) -> str:
        """String representation of the loan."""
        return f"Loan {self._loan_id[:8]}... - User: {self._user_id}, Item: {self._item_id}, Status: {self.get_status()}"
    
    def __repr__(self) -> str:
        """Developer-friendly representation of the loan."""
        return f"Loan(loan_id='{self._loan_id}', user_id='{self._user_id}', item_id='{self._item_id}', status='{self.get_status()}')"
    
    def __eq__(self, other) -> bool:
        """Check equality based on loan ID."""
        if not isinstance(other, Loan):
            return False
        return self._loan_id == other._loan_id
    
    def __hash__(self) -> int:
        """Hash based on loan ID for use in sets and dictionaries."""
        return hash(self._loan_id) 