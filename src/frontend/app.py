"""
Streamlit app for AE1 Library Management System.

This module provides the web interface for the library management system,
with separate interfaces for members and staff.
"""

import streamlit as st
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.library_system import LibrarySystem
from database.database_manager import DatabaseManager
from frontend.member_interface import render_member_interface
from frontend.staff_interface import render_staff_interface


def initialise_session_state():
    """Initialise session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'library_system' not in st.session_state:
        st.session_state.library_system = None
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = None


def initialise_system():
    """Initialise the library system and database manager."""
    if st.session_state.library_system is None:
        st.session_state.library_system = LibrarySystem("Northeastern University Library")
        st.session_state.db_manager = DatabaseManager("library.db")
        
        # Load data from database into the library system
        load_data_from_database()


def load_data_from_database():
    """Load users, items, and loans from the database into the library system."""
    try:
        # Load users
        users = st.session_state.db_manager.get_all_users()
        for user in users:
            st.session_state.library_system.register_user(user)
        
        # Load items
        items = st.session_state.db_manager.get_all_items()
        for item in items:
            st.session_state.library_system.add_item(item)
        
        # Load active loans and restore system state
        all_loans = []
        for user in users:
            user_loans = st.session_state.db_manager.get_loans_by_user(user.user_id)
            all_loans.extend(user_loans)
        
        # Add loans to the system
        for loan in all_loans:
            st.session_state.library_system._loans[loan.loan_id] = loan
            if not loan.is_returned:
                if loan.user_id not in st.session_state.library_system._active_loans:
                    st.session_state.library_system._active_loans[loan.user_id] = []
                st.session_state.library_system._active_loans[loan.user_id].append(loan.loan_id)
                
                # Update item availability
                item = st.session_state.library_system.get_item(loan.item_id)
                if item:
                    item._is_available = False
        
    except Exception as e:
        st.error(f"Error loading data from database: {e}")


def authenticate_user(user_id: str):
    """Authenticate a user and set session state."""
    user = st.session_state.library_system.get_user(user_id)
    if user:
        st.session_state.authenticated = True
        st.session_state.user = user
        return True
    return False


def render_login_page():
    """Render the login page."""
    st.title("Northeastern University Library Management System")
    st.subheader("User Authentication")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.write("Enter your User ID to access the system:")
            user_id = st.text_input("User ID", placeholder="M001 for members, S001 for staff")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if user_id:
                    if authenticate_user(user_id):
                        st.success(f"Welcome, {st.session_state.user.name}!")
                        st.rerun()
                    else:
                        st.error("Invalid User ID. Please try again.")
                else:
                    st.warning("Please enter a User ID.")
    
    # Show demo instructions
    st.markdown("---")
    st.subheader("Demo Instructions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Member Login Examples:**")
        st.code("""
M001 - Marcelo Amorelli
M002 - Umar Hussain
M003 - Carol Davis
M004 - David Wilson 
M005 - Emma Brown
        """)
    
    with col2:
        st.write("**Staff Login Examples:**")
        st.code("""
S001 - Jiri Motejlek (Manager)
S002 - Michael Rodriguez (Librarian)
S003 - Jennifer Martinez (Librarian)
S004 - Robert Thompson (Manager)
S005 - Lisa Garcia (Librarian)
        """)
    
    with st.expander("System Information"):
        st.write("""
        **Library Management System Demo**
        
        Demonstrates object-oriented programming principles including:
        - Abstract classes and inheritance
        - Polymorphism and encapsulation
        - Static attributes and methods
        
        **User Types:**
        - **Members**: Can browse, borrow, return items (5-item limit)
        - **Staff**: Managers (full access) and Librarians (item management)
        
        **Item Types:** Books (21-day loans), Magazines (7-day loans), DVDs (14-day loans)
        
        **Note:** Demo system with simplified authentication. Please do not hack my system and steal my books.
        """)


def render_header():
    """Render the application header."""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("Library Management System")
        if st.session_state.user:
            st.write(f"Welcome, **{st.session_state.user.name}** ({st.session_state.user.get_role()})")
    
    with col3:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()


def main():
    """Main application function."""
    st.set_page_config(
        page_title="Library Management System",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialise session state and system
    initialise_session_state()
    initialise_system()
    
    # Check authentication
    if not st.session_state.authenticated:
        render_login_page()
    else:
        render_header()
        
        # Route to appropriate interface based on user role
        if st.session_state.user.get_role() == "Member":
            render_member_interface()
        elif st.session_state.user.get_role() == "Staff":
            render_staff_interface()
        else:
            st.error("Unknown user role. Please contact the administrator.")


if __name__ == "__main__":
    main() 