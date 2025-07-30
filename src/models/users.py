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
    Member class inheriting from User.
    
    Demonstrates:
    - Inheritance from abstract base class
    - Method overriding with member-specific behavior
    - Member-specific borrowing limits and history tracking
    """
    
    # Static attributes for member limits
    _default_borrowing_limit = 5
    _total_members = 0
    
    def __init__(self, user_id: str, name: str, email: str, phone: Optional[str] = None):
        """
        Initialise a member.
        
        Args:
            user_id: Unique identifier for the member
            name: Full name of the member
            email: Email address of the member
            phone: Phone number (optional)
        """
        super().__init__(user_id, name, email)
        self._phone = phone
        self._borrowed_items: List[str] = []  # List of item IDs currently borrowed
        self._loan_history: List[str] = []  # List of loan IDs for history
        self._fines_owed = 0.0
        self._membership_expiry = datetime.now() + timedelta(days=365)  # 1 year from now
        
        # Increment member-specific counter
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
    def get_borrowing_limit(self) -> int:
        """
        Get the borrowing limit for this member.
        
        Returns:
            int: Maximum number of items this member can borrow
        """
        return self._default_borrowing_limit  # All members get 5 items
    
    def get_role(self) -> str:
        """
        Get the role of the user.
        
        Returns:
            str: "Member"
        """
        return "Member"
    
    def can_borrow_item(self, item: 'LibraryItem') -> bool:
        """
        Check if the member can borrow a specific item.
        
        Args:
            item: The library item to check
            
        Returns:
            bool: True if member can borrow the item, False otherwise
        """
        # Check if member has reached borrowing limit
        if len(self._borrowed_items) >= self.get_borrowing_limit():
            return False
        
        # Check if item is available
        if not item.is_available:
            return False
        
        # Check if membership is active
        if datetime.now() > self._membership_expiry:
            return False
        
        # Check if member has outstanding fines (limit borrowing if fines > $10)
        if self._fines_owed > 10.0:
            return False
        
        return True
    
    # Member-specific methods
    def borrow_item(self, item_id: str) -> bool:
        """
        Borrow an item.
        
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
        Return a borrowed item.
        
        Args:
            item_id: ID of the item to return
            
        Returns:
            bool: True if item was successfully returned, False otherwise
        """
        if item_id in self._borrowed_items:
            self._borrowed_items.remove(item_id)
            return True
        
        return False
    
    def add_loan_to_history(self, loan_id: str) -> None:
        """
        Add a loan to the member's history.
        
        Args:
            loan_id: ID of the loan to add to history
        """
        if loan_id not in self._loan_history:
            self._loan_history.append(loan_id)
    
    def add_fine(self, amount: float) -> None:
        """
        Add a fine to the member's account.
        
        Args:
            amount: Fine amount to add
        """
        if amount > 0:
            self._fines_owed += amount
    
    def pay_fine(self, amount: float) -> bool:
        """
        Pay a fine.
        
        Args:
            amount: Amount to pay
            
        Returns:
            bool: True if payment was successful, False otherwise
        """
        if amount <= 0 or amount > self._fines_owed:
            return False
        
        self._fines_owed -= amount
        return True
    
    def is_membership_active(self) -> bool:
        """
        Check if the membership is currently active.
        
        Returns:
            bool: True if membership is active, False otherwise
        """
        return datetime.now() <= self._membership_expiry
    
    def renew_membership(self, months: int = 12) -> None:
        """
        Renew the membership.
        
        Args:
            months: Number of months to extend the membership
        """
        if months <= 0:
            raise ValueError("Renewal period must be positive")
        
        if self.is_membership_active():
            self._membership_expiry += timedelta(days=30 * months)
        else:
            self._membership_expiry = datetime.now() + timedelta(days=30 * months)
    
    def __str__(self) -> str:
        """String representation of the member."""
        status = "Active" if self.is_membership_active() else "Expired"
        items_count = len(self._borrowed_items)
        return f"Member: {self._name} - {items_count} items borrowed, {status}"


class Staff(User):
    """
    Staff class inheriting from User.
    
    Demonstrates:
    - Inheritance from abstract base class
    - Method overriding with staff-specific privileges
    - Staff-specific administrative capabilities
    """
    
    # Static attributes for staff
    _total_staff = 0
    
    def __init__(self, user_id: str, name: str, email: str, role: str = "Librarian",
                 hire_date: Optional[datetime] = None):
        """
        Initialise a staff member.
        
        Args:
            user_id: Unique identifier for the staff member
            name: Full name of the staff member
            email: Email address of the staff member
            role: Role/position of the staff member (Manager or Librarian)
            hire_date: Date when staff member was hired
        """
        super().__init__(user_id, name, email)
        self._role = role
        self._hire_date = hire_date or datetime.now()
        self._permissions = self._get_default_permissions()
        
        # Staff can borrow more items than regular members
        self._borrowed_items: List[str] = []
        
        # Increment staff-specific counter
        Staff._total_staff += 1
    
    # Properties for staff-specific attributes
    @property
    def staff_role(self) -> str:
        """Get the staff role/position."""
        return self._role
    
    @staff_role.setter
    def staff_role(self, value: str):
        """Set the staff role with validation."""
        valid_roles = ["Manager", "Librarian"]
        if value not in valid_roles:
            raise ValueError(f"Staff role must be one of: {', '.join(valid_roles)}")
        self._role = value
        self._permissions = self._get_default_permissions()  # Update permissions
    

    
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