"""
Concrete implementations of User subclasses.

This module contains the specific types of users that inherit from
the User abstract base class, demonstrating inheritance and role-based polymorphism.
"""

from datetime import datetime, timedelta
from typing import List, Optional, TYPE_CHECKING
from .abstract_classes import User

if TYPE_CHECKING:
    from .abstract_classes import LibraryItem
    from .loan import Loan


class Member(User):
    """
    Regular library member with borrowing privileges.
    
    Inherits from User and implements member-specific borrowing logic.
    """
    
    # Static attributes for member limits
    _default_borrowing_limit = 5
    _total_members = 0
    
    def __init__(self, user_id: str, name: str, email: str, phone: Optional[str] = None):
        """Create a new library member."""
        super().__init__(user_id, name, email)
        self._phone = phone
        self._borrowed_items: List[str] = []  # List of item IDs currently borrowed
        self._loan_history: List[str] = []  # List of loan IDs for history
        self._fines_owed = 0.0
        self._membership_expiry = datetime.now() + timedelta(days=365)  # 1 year from now
        
        # count total members
        Member._total_members += 1
    
    # Properties for member-specific attributes
    @property
    def phone(self) -> Optional[str]:
        """Get the member phone number."""
        return self._phone
    
    @phone.setter
    def phone(self, value: Optional[str]):
        """Set the member phone number."""
        self._phone = value.strip() if value else None
    

    
    @property
    def borrowed_items(self) -> List[str]:
        """Get the list of currently borrowed item IDs."""
        return self._borrowed_items.copy()  # Return copy to prevent external modification
    
    @property
    def loan_history(self) -> List[str]:
        """Get the loan history."""
        return self._loan_history.copy()
    
    @property
    def fines_owed(self) -> float:
        """Get the amount of fines owed."""
        return self._fines_owed
    
    @property
    def membership_expiry(self) -> datetime:
        """Get the membership expiry date."""
        return self._membership_expiry
    
    @staticmethod
    def get_total_members() -> int:
        """Get the total number of members registered."""
        return Member._total_members
    
    # Override abstract methods (polymorphism)
    def get_borrowing_limit(self):
        """Max items this member can borrow at once."""
        return self._default_borrowing_limit  # All members get 5 items
    
    def get_role(self):
        """Returns 'Member'."""
        return "Member"
    
    def can_borrow_item(self, item):
        """Check if member can borrow this item (based on limits and availability)."""
        if not item.is_available:
            return False
        
        current_loans = len(self._borrowed_items)
        if current_loans >= self.get_borrowing_limit():
            return False  # already at limit
        
        return True
    
    def add_borrowed_item(self, item_id: str) -> bool:
        """Add an item to borrowed list."""
        if item_id not in self._borrowed_items:
            self._borrowed_items.append(item_id)
            return True
        return False
    
    def remove_borrowed_item(self, item_id: str) -> bool:
        """Remove an item from borrowed list."""
        if item_id in self._borrowed_items:
            self._borrowed_items.remove(item_id)
            return True
        return False
    
    def add_fine(self, amount: float):
        """Add to fines owed."""
        self._fines_owed += amount
    
    def pay_fines(self, amount: float) -> float:
        """Pay some fines. Returns remaining balance."""
        self._fines_owed = max(0, self._fines_owed - amount)
        return self._fines_owed
    
    def is_membership_active(self) -> bool:
        """Check if membership is still valid."""
        return datetime.now() < self._membership_expiry
    
    def extend_membership(self, days: int = 365):
        """Extend membership by specified days."""
        self._membership_expiry += timedelta(days=days)
    
    def add_to_loan_history(self, loan_id: str):
        """Add loan to history."""
        if loan_id not in self._loan_history:
            self._loan_history.append(loan_id)
    
    def get_borrowing_statistics(self) -> dict:
        """Get member borrowing stats."""
        return {
            'total_loans': len(self._loan_history),
            'active_loans': len(self._borrowed_items),
            'fines_owed': self._fines_owed,
            'membership_active': self.is_membership_active(),
            'borrowing_limit': self.get_borrowing_limit()
        }
    
    def to_dict(self) -> dict:
        """Convert to dict for storage."""
        return {
            'user_id': self._user_id,
            'name': self._name,
            'email': self._email,
            'role': 'Member',
            'phone': self._phone,
            'registration_date': self._registration_date.isoformat(),
            'membership_expiry': self._membership_expiry.isoformat(),
            'borrowed_items': self._borrowed_items.copy(),
            'loan_history': self._loan_history.copy(),
            'fines_owed': self._fines_owed
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create member from dict."""
        member = cls(
            user_id=data['user_id'],
            name=data['name'],
            email=data['email'],
            phone=data.get('phone')
        )
        
        # restore saved data
        if 'registration_date' in data:
            member._registration_date = datetime.fromisoformat(data['registration_date'])
        if 'membership_expiry' in data:
            member._membership_expiry = datetime.fromisoformat(data['membership_expiry'])
        
        member._borrowed_items = data.get('borrowed_items', [])
        member._loan_history = data.get('loan_history', [])
        member._fines_owed = data.get('fines_owed', 0.0)
        
        return member
    
    def __str__(self) -> str:
        """String representation of the member."""
        status = "Active" if self.is_membership_active() else "Expired"
        items_count = len(self._borrowed_items)
        return f"Member: {self._name} - {items_count} items borrowed, {status}"


class Staff(User):
    """
    Library staff with administrative privileges.
    
    Different staff roles (Manager/Librarian) have different permissions.
    """
    
    # Static attributes for staff
    _total_staff = 0
    
    def __init__(self, user_id: str, name: str, email: str, role: str = "Librarian",
                 hire_date: Optional[datetime] = None):
        """Create a new staff member with role and hire date."""
        super().__init__(user_id, name, email)
        self._role = role
        self._hire_date = hire_date or datetime.now()
        self._permissions = self._get_default_permissions()
        
        # staff get higher borrowing limits
        self._borrowed_items: List[str] = []
        
        # track staff count
        Staff._total_staff += 1
    
    # Properties for staff-specific attributes
    @property
    def staff_role(self) -> str:
        """Get the staff role/position."""
        return self._role
    
    @staff_role.setter
    def staff_role(self, value: str):
        """Set staff role (Manager or Librarian only)."""
        valid_roles = ["Manager", "Librarian"]
        if value not in valid_roles:
            raise ValueError(f"Invalid role: {value}")
        self._role = value
        self._permissions = self._get_default_permissions()  # refresh permissions
    

    
    @property
    def hire_date(self) -> datetime:
        """Get the staff hire date."""
        return self._hire_date
    
    @property
    def permissions(self) -> List[str]:
        """Get the staff permissions."""
        return self._permissions.copy()
    
    @staticmethod
    def get_total_staff() -> int:
        """Get the total number of staff members."""
        return Staff._total_staff
    
    def _get_default_permissions(self) -> List[str]:
        """
        Get default permissions based on staff role.
        
        Returns:
            List[str]: List of permissions for this staff role
        """
        base_permissions = ["view_catalog", "help_members"]
        
        if self._role == "Manager":
            return base_permissions + [
                "add_items", "remove_items", "manage_users", "view_reports",
                "system_admin", "manage_fines"
            ]
        elif self._role == "Librarian":
            return base_permissions + [
                "add_items", "remove_items", "check_out_items", "check_in_items",
                "view_member_history", "manage_fines"
            ]
        else:
            return base_permissions
    
    # Override abstract methods (polymorphism)
    def get_borrowing_limit(self) -> int:
        """
        Get the borrowing limit for staff members.
        Staff members have higher borrowing limits.
        
        Returns:
            int: Maximum number of items this staff member can borrow
        """
        if self._role == "Manager":
            return 20
        else:  # Librarian
            return 15
    
    def get_role(self) -> str:
        """
        Get the role of the user.
        
        Returns:
            str: "Staff"
        """
        return "Staff"
    
    def can_borrow_item(self, item: 'LibraryItem') -> bool:
        """
        Check if the staff member can borrow a specific item.
        Staff have fewer restrictions than regular members.
        
        Args:
            item: The library item to check
            
        Returns:
            bool: True if staff can borrow the item, False otherwise
        """
        # Check if staff has reached borrowing limit
        if len(self._borrowed_items) >= self.get_borrowing_limit():
            return False
        
        # Check if item is available
        if not item.is_available:
            return False
        
        # Staff don't have membership expiry or fine restrictions
        return True
    
    # Staff-specific methods
    def has_permission(self, permission: str) -> bool:
        """
        Check if the staff member has a specific permission.
        
        Args:
            permission: The permission to check
            
        Returns:
            bool: True if staff has the permission, False otherwise
        """
        return permission in self._permissions
    
    def add_permission(self, permission: str) -> bool:
        """
        Add a permission to the staff member.
        
        Args:
            permission: Permission to add
            
        Returns:
            bool: True if permission was added, False if already exists
        """
        if permission not in self._permissions:
            self._permissions.append(permission)
            return True
        return False
    
    def remove_permission(self, permission: str) -> bool:
        """
        Remove a permission from the staff member.
        
        Args:
            permission: Permission to remove
            
        Returns:
            bool: True if permission was removed, False if not found
        """
        if permission in self._permissions:
            self._permissions.remove(permission)
            return True
        return False
    
    def can_manage_inventory(self) -> bool:
        """
        Check if the staff member can manage inventory.
        
        Returns:
            bool: True if staff can manage inventory, False otherwise
        """
        return self.has_permission("add_items") and self.has_permission("remove_items")
    
    def can_manage_users(self) -> bool:
        """
        Check if the staff member can manage users.
        
        Returns:
            bool: True if staff can manage users, False otherwise
        """
        return self.has_permission("manage_users")
    
    def can_view_member_activity(self) -> bool:
        """
        Check if the staff member can view member activity.
        
        Returns:
            bool: True if staff can view member activity, False otherwise
        """
        return self.has_permission("view_member_history")
    
    def borrow_item(self, item_id: str) -> bool:
        """
        Borrow an item as a staff member.
        
        Args:
            item_id: ID of the item to borrow
            
        Returns:
            bool: True if item was successfully borrowed, False otherwise
        """
        if len(self._borrowed_items) >= self.get_borrowing_limit():
            return False
        
        if item_id not in self._borrowed_items:
            self._borrowed_items.append(item_id)
            return True
        
        return False
    
    def return_item(self, item_id: str) -> bool:
        """
        Return a borrowed item as a staff member.
        
        Args:
            item_id: ID of the item to return
            
        Returns:
            bool: True if item was successfully returned, False otherwise
        """
        if item_id in self._borrowed_items:
            self._borrowed_items.remove(item_id)
            return True
        
        return False
    
    def get_years_of_service(self) -> float:
        """
        Calculate years of service.
        
        Returns:
            float: Number of years the staff member has been employed
        """
        service_duration = datetime.now() - self._hire_date
        return round(service_duration.days / 365.25, 1)  # Account for leap years
    
    def __str__(self) -> str:
        """String representation of the staff member."""
        years_service = self.get_years_of_service()
        items_count = len(self._borrowed_items)
        return f"Staff: {self._name} ({self._role}) - {years_service} years service, {items_count} items borrowed" 