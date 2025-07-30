"""
Staff interface for the Library Management System.

This module provides the Streamlit interface for library staff to manage
inventory, users, loans, and generate reports.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List
from models.items import Book, Magazine, DVD
from models.users import Member, Staff
from models.loan import Loan


def render_staff_interface():
    """Render the main staff interface."""
    staff = st.session_state.user
    library = st.session_state.library_system
    
    # Sidebar navigation
    st.sidebar.title("Staff Menu")
    
    menu_options = [
        "Dashboard",
        "Manage Items",
        "Manage Users", 
        "Loan Management",
        "Reports",
        "System Settings"
    ]
    
    selected_page = st.sidebar.radio("Navigate to:", menu_options)
    
    # Display staff permissions in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Your Permissions")
    
    if staff.can_manage_inventory():
        st.sidebar.success("Manage Inventory")
    if staff.can_manage_users():
        st.sidebar.success("Manage Users")
    if staff.can_view_member_activity():
        st.sidebar.success("View Member Activity")
    
    # Render selected page
    if selected_page == "Dashboard":
        render_staff_dashboard()
    elif selected_page == "Manage Items":
        render_manage_items()
    elif selected_page == "Manage Users":
        render_manage_users()
    elif selected_page == "Loan Management":
        render_loan_management()
    elif selected_page == "Reports":
        render_reports()
    elif selected_page == "System Settings":
        render_system_settings()


def render_staff_dashboard():
    """Render the staff dashboard."""
    st.subheader("Staff Dashboard")
    
    library = st.session_state.library_system
    staff = st.session_state.user
    
    # System statistics
    stats = library.get_system_statistics()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Items", stats['total_items'])
        st.metric("Available", stats['available_items'])
    
    with col2:
        st.metric("Total Users", stats['total_users'])
        st.metric("Members", stats['total_members'])
    
    with col3:
        st.metric("Active Loans", stats['active_loans'])
        st.metric("Overdue", stats['overdue_loans'])
    
    with col4:
        st.metric("Total Fines", f"${stats['total_fines_owed']:.2f}")
        st.metric("Staff", stats['total_staff'])
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Overdue loans alert
    overdue_loans = library.get_overdue_loans()
    if overdue_loans:
        st.warning(f"ALERT: {len(overdue_loans)} overdue loans require attention!")
        
        with st.expander("View Overdue Loans"):
            overdue_data = []
            for loan in overdue_loans[:10]:  # Show first 10
                user = library.get_user(loan.user_id)
                item = library.get_item(loan.item_id)
                if user and item:
                    overdue_data.append({
                        "User": user.name,
                        "Item": item.title,
                        "Type": item.get_item_type(),
                        "Due Date": loan.date_due.strftime("%Y-%m-%d"),
                        "Days Overdue": loan.days_overdue(),
                        "Fine": f"${loan.fine_amount:.2f}"
                    })
            
            if overdue_data:
                df = pd.DataFrame(overdue_data)
                st.dataframe(df, use_container_width=True)
    
    # Popular items
    st.subheader("Most Popular Items")
    popular_items = library.get_popular_items(5)
    
    if popular_items:
        popular_data = []
        for item, count in popular_items:
            popular_data.append({
                "Title": item.title,
                "Type": item.get_item_type(),
                "Loans": count,
                "Status": "Available" if item.is_available else "Checked Out"
            })
        
        df = pd.DataFrame(popular_data)
        st.dataframe(df, use_container_width=True)
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Add New Item", use_container_width=True):
            st.session_state.show_add_item = True
            st.rerun()
    
    with col2:
        if st.button("Register New User", use_container_width=True):
            st.session_state.show_add_user = True
            st.rerun()
    
    with col3:
        if st.button("Generate Report", use_container_width=True):
            st.session_state.selected_page = "Reports"
            st.rerun()


def render_manage_items():
    """Render the item management interface."""
    st.subheader("Manage Library Items")
    
    staff = st.session_state.user
    library = st.session_state.library_system
    
    if not staff.can_manage_inventory():
        st.error("You do not have permission to manage inventory.")
        return
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["View Items", "Add Item", "Edit/Remove"])
    
    with tab1:
        render_view_items()
    
    with tab2:
        render_add_item()
    
    with tab3:
        render_edit_remove_items()


def render_view_items():
    """Render the view items interface."""
    library = st.session_state.library_system
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        type_filter = st.selectbox("Filter by Type", ["All", "Book", "Magazine", "DVD"])
    
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "Available", "Checked Out"])
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Title", "Type", "Date Added", "Availability"])
    
    # Get and filter items
    all_items = library.get_all_items()
    filtered_items = []
    
    for item in all_items:
        if type_filter != "All" and item.get_item_type() != type_filter:
            continue
        if status_filter == "Available" and not item.is_available:
            continue
        elif status_filter == "Checked Out" and item.is_available:
            continue
        filtered_items.append(item)
    
    # Sort items
    if sort_by == "Title":
        filtered_items.sort(key=lambda x: x.title)
    elif sort_by == "Type":
        filtered_items.sort(key=lambda x: x.get_item_type())
    elif sort_by == "Date Added":
        filtered_items.sort(key=lambda x: x.date_added, reverse=True)
    elif sort_by == "Availability":
        filtered_items.sort(key=lambda x: x.is_available, reverse=True)
    
    st.write(f"Showing {len(filtered_items)} items")
    
    # Create table data
    items_data = []
    for item in filtered_items:
        status = "Available" if item.is_available else "Checked Out"
        
        items_data.append({
            "ID": item.item_id,
            "Title": item.title,
            "Type": item.get_item_type(),
            "Status": status,
            "Date Added": item.date_added.strftime("%Y-%m-%d")
        })
    
    if items_data:
        df = pd.DataFrame(items_data)
        st.dataframe(df, use_container_width=True)


def render_add_item():
    """Render the add item interface."""
    st.write("Add a new item to the library:")
    
    with st.form("add_item_form"):
        item_type = st.selectbox("Item Type", ["Book", "Magazine", "DVD"])
        
        # Common fields
        item_id = st.text_input("Item ID*", placeholder="B011, M009, D011")
        title = st.text_input("Title*", placeholder="Enter the title")
        
        # Type-specific fields
        if item_type == "Book":
            author = st.text_input("Author*", placeholder="Enter author name")
            isbn = st.text_input("ISBN", placeholder="Enter ISBN")
            pages = st.number_input("Pages", min_value=0, value=0)
        
        elif item_type == "Magazine":
            issue_number = st.text_input("Issue Number*", placeholder="Issue 1, Jan 2024")
            publisher = st.text_input("Publisher*", placeholder="Enter publisher name")
            pub_date = st.date_input("Publication Date", value=datetime.now().date())
        
        elif item_type == "DVD":
            duration = st.number_input("Duration (minutes)*", min_value=1, value=90)
            genre = st.text_input("Genre*", placeholder="Action, Drama, Comedy")
            director = st.text_input("Director", placeholder="Enter director name")
            rating = st.selectbox("Rating", ["", "G", "PG", "PG-13", "R", "NC-17", "NR"])
        
        submitted = st.form_submit_button("Add Item")
        
        if submitted:
            if not item_id or not title:
                st.error("Item ID and Title are required fields.")
            else:
                success = add_new_item(item_type, item_id, title, locals())
                if success:
                    st.success(f"{item_type} '{title}' added successfully!")
                    st.rerun()


def render_edit_remove_items():
    """Render the edit/remove items interface."""
    library = st.session_state.library_system
    
    st.write("Select an item to edit or remove:")
    
    # Item selection
    all_items = library.get_all_items()
    item_options = {f"{item.item_id} - {item.title}": item for item in all_items}
    
    if item_options:
        selected_item_key = st.selectbox("Select Item", list(item_options.keys()))
        selected_item = item_options[selected_item_key]
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Edit Item", use_container_width=True):
                st.session_state.editing_item = selected_item
                st.rerun()
        
        with col2:
            if selected_item.is_available:
                if st.button("Remove Item", use_container_width=True):
                    if remove_item(selected_item.item_id):
                        st.success(f"Item '{selected_item.title}' removed successfully!")
                        st.rerun()
            else:
                st.warning("Cannot remove item - currently checked out")


def render_manage_users():
    """Render the user management interface."""
    st.subheader("Manage Users")
    
    staff = st.session_state.user
    library = st.session_state.library_system
    
    if not staff.can_manage_users():
        st.error("You do not have permission to manage users.")
        return
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["View Users", "Register User", "User Details"])
    
    with tab1:
        render_view_users()
    
    with tab2:
        render_register_user()
    
    with tab3:
        render_user_details()


def render_view_users():
    """Render the view users interface."""
    library = st.session_state.library_system
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        role_filter = st.selectbox("Filter by Role", ["All", "Member", "Staff"])
    
    with col2:
        type_filter = "All"
    
    # Get and filter users
    all_users = library.get_all_users()
    filtered_users = []
    
    for user in all_users:
        if role_filter != "All" and user.get_role() != role_filter:
            continue
        

        
        filtered_users.append(user)
    
    st.write(f"Showing {len(filtered_users)} users")
    
    # Create table data
    users_data = []
    for user in filtered_users:
        if user.get_role() == "Member":
            status = "Active" if user.is_membership_active() else "Expired"
            extra_info = "Member"
        else:
            status = "Active"
            extra_info = user.staff_role if hasattr(user, 'staff_role') else "Staff"
        
        users_data.append({
            "ID": user.user_id,
            "Name": user.name,
            "Email": user.email,
            "Role": user.get_role(),
            "Type/Position": extra_info,
            "Status": status,
            "Registration": user.registration_date.strftime("%Y-%m-%d")
        })
    
    if users_data:
        df = pd.DataFrame(users_data)
        st.dataframe(df, use_container_width=True)


def render_register_user():
    """Render the register user interface."""
    st.write("Register a new user:")
    
    with st.form("register_user_form"):
        user_type = st.selectbox("User Type", ["Member", "Staff"])
        
        # Common fields
        user_id = st.text_input("User ID*", placeholder="M011, S006")
        name = st.text_input("Full Name*", placeholder="Enter full name")
        email = st.text_input("Email*", placeholder="Enter email address")
        
        if user_type == "Member":
            phone = st.text_input("Phone", placeholder="Enter phone number")
        
        elif user_type == "Staff":
            staff_role = st.selectbox("Staff Role", ["Manager", "Librarian"])
            hire_date = st.date_input("Hire Date", value=datetime.now().date())
        
        submitted = st.form_submit_button("Register User")
        
        if submitted:
            if not user_id or not name or not email:
                st.error("User ID, Name, and Email are required fields.")
            else:
                success = register_new_user(user_type, user_id, name, email, locals())
                if success:
                    st.success(f"{user_type} '{name}' registered successfully!")
                    st.rerun()


def render_user_details():
    """Render detailed user information and management."""
    library = st.session_state.library_system
    
    # User selection
    all_users = library.get_all_users()
    user_options = {f"{user.user_id} - {user.name}": user for user in all_users}
    
    if user_options:
        selected_user_key = st.selectbox("Select User", list(user_options.keys()))
        selected_user = user_options[selected_user_key]
        
        # Display user information
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**User Information**")
            st.write(f"Name: {selected_user.name}")
            st.write(f"Email: {selected_user.email}")
            st.write(f"Role: {selected_user.get_role()}")
            st.write(f"Registration: {selected_user.registration_date.strftime('%Y-%m-%d')}")
            
            if selected_user.get_role() == "Member":
                st.write(f"Phone: {selected_user.phone or 'Not provided'}")
                status = "Active" if selected_user.is_membership_active() else "Expired"
                st.write(f"Status: {status}")
                st.write(f"Fines Owed: ${selected_user.fines_owed:.2f}")
        
        with col2:
            st.write("**Activity Summary**")
            activity_report = library.get_member_activity_report(selected_user.user_id)
            
            if activity_report:
                st.write(f"Total Loans: {activity_report['total_loans']}")
                st.write(f"Active Loans: {activity_report['active_loans']}")
                st.write(f"Overdue Loans: {activity_report['overdue_loans']}")
                st.write(f"Borrowing Limit: {activity_report['borrowing_limit']}")
        
        # Loan history
        st.subheader("Loan History")
        user_loans = library.get_user_loans(selected_user.user_id, active_only=False)
        
        if user_loans:
            loan_data = []
            for loan in user_loans[-10:]:  # Show last 10 loans
                item = library.get_item(loan.item_id)
                if item:
                    status = "Returned" if loan.is_returned else "Active"
                    loan_data.append({
                        "Item": item.title,
                        "Type": item.get_item_type(),
                        "Borrowed": loan.date_borrowed.strftime("%Y-%m-%d"),
                        "Due": loan.date_due.strftime("%Y-%m-%d"),
                        "Returned": loan.date_returned.strftime("%Y-%m-%d") if loan.date_returned else "N/A",
                        "Status": status,
                        "Fine": f"${loan.fine_amount:.2f}" if loan.fine_amount > 0 else "None"
                    })
            
            if loan_data:
                df = pd.DataFrame(loan_data)
                st.dataframe(df, use_container_width=True)


def render_loan_management():
    """Render the loan management interface."""
    st.subheader("Loan Management")
    
    library = st.session_state.library_system
    
    # Tabs for different loan management tasks
    tab1, tab2, tab3 = st.tabs(["Active Loans", "Overdue Loans", "Loan History"])
    
    with tab1:
        render_active_loans()
    
    with tab2:
        render_overdue_loans()
    
    with tab3:
        render_loan_history()


def render_active_loans():
    """Render active loans management."""
    library = st.session_state.library_system
    
    # Get all active loans
    all_active_loans = []
    for user in library.get_all_users():
        user_loans = library.get_user_loans(user.user_id, active_only=True)
        all_active_loans.extend(user_loans)
    
    if all_active_loans:
        loan_data = []
        for loan in all_active_loans:
            user = library.get_user(loan.user_id)
            item = library.get_item(loan.item_id)
            
            if user and item:
                days_remaining = (loan.date_due - datetime.now()).days
                status = "Overdue" if loan.is_overdue() else "Active"
                
                loan_data.append({
                    "User": user.name,
                    "Item": item.title,
                    "Type": item.get_item_type(),
                    "Borrowed": loan.date_borrowed.strftime("%Y-%m-%d"),
                    "Due": loan.date_due.strftime("%Y-%m-%d"),
                    "Days Remaining": days_remaining,
                    "Status": status,
                    "Renewals": loan.renewal_count
                })
        
        df = pd.DataFrame(loan_data)
        st.dataframe(df, use_container_width=True)
        
        st.write(f"Total active loans: {len(all_active_loans)}")
    else:
        st.info("No active loans.")


def render_overdue_loans():
    """Render overdue loans management."""
    library = st.session_state.library_system
    
    overdue_loans = library.get_overdue_loans()
    
    if overdue_loans:
        st.warning(f"There are {len(overdue_loans)} overdue loans requiring attention.")
        
        overdue_data = []
        for loan in overdue_loans:
            user = library.get_user(loan.user_id)
            item = library.get_item(loan.item_id)
            
            if user and item:
                overdue_data.append({
                    "User": user.name,
                    "Contact": user.email,
                    "Item": item.title,
                    "Type": item.get_item_type(),
                    "Due Date": loan.date_due.strftime("%Y-%m-%d"),
                    "Days Overdue": loan.days_overdue(),
                    "Fine": f"${loan.fine_amount:.2f}"
                })
        
        df = pd.DataFrame(overdue_data)
        st.dataframe(df, use_container_width=True)
        
        # Summary statistics
        total_fines = sum(loan.fine_amount for loan in overdue_loans)
        avg_days_overdue = sum(loan.days_overdue() for loan in overdue_loans) / len(overdue_loans)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Fines Owed", f"${total_fines:.2f}")
        with col2:
            st.metric("Average Days Overdue", f"{avg_days_overdue:.1f}")
    else:
        st.success("No overdue loans!")


def render_loan_history():
    """Render loan history and statistics."""
    library = st.session_state.library_system
    
    # Get all loans
    all_loans = []
    for user in library.get_all_users():
        user_loans = library.get_user_loans(user.user_id, active_only=False)
        all_loans.extend(user_loans)
    
    if all_loans:
        # Summary statistics
        total_loans = len(all_loans)
        completed_loans = len([loan for loan in all_loans if loan.is_returned])
        total_fines = sum(loan.fine_amount for loan in all_loans if loan.fine_amount > 0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Loans", total_loans)
        with col2:
            st.metric("Completed Loans", completed_loans)
        with col3:
            st.metric("Total Fines Collected", f"${total_fines:.2f}")
        
        # Recent loans
        st.subheader("Recent Loan Activity")
        recent_loans = sorted(all_loans, key=lambda x: x.date_borrowed, reverse=True)[:20]
        
        recent_data = []
        for loan in recent_loans:
            user = library.get_user(loan.user_id)
            item = library.get_item(loan.item_id)
            
            if user and item:
                status = "Returned" if loan.is_returned else "Active"
                recent_data.append({
                    "User": user.name,
                    "Item": item.title,
                    "Type": item.get_item_type(),
                    "Borrowed": loan.date_borrowed.strftime("%Y-%m-%d"),
                    "Status": status,
                    "Duration": loan.get_loan_duration() if loan.is_returned else "Ongoing"
                })
        
        df = pd.DataFrame(recent_data)
        st.dataframe(df, use_container_width=True)


def render_reports():
    """Render the reports interface."""
    st.subheader("System Reports")
    
    library = st.session_state.library_system
    
    # Report type selection
    report_type = st.selectbox(
        "Select Report Type",
        ["System Overview", "Popular Items", "User Activity", "Financial Report", "Inventory Status"]
    )
    
    if report_type == "System Overview":
        render_system_overview_report()
    elif report_type == "Popular Items":
        render_popular_items_report()
    elif report_type == "User Activity":
        render_user_activity_report()
    elif report_type == "Financial Report":
        render_financial_report()
    elif report_type == "Inventory Status":
        render_inventory_status_report()


def render_system_overview_report():
    """Render system overview report."""
    library = st.session_state.library_system
    stats = library.get_system_statistics()
    
    st.write("**Library System Overview**")
    st.write(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Key metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Collection Statistics**")
        st.write(f"Total Items: {stats['total_items']}")
        st.write(f"Available Items: {stats['available_items']}")
        st.write(f"Books: {stats['books_count']}")
        st.write(f"Magazines: {stats['magazines_count']}")
        st.write(f"DVDs: {stats['dvds_count']}")
    
    with col2:
        st.write("**User Statistics**")
        st.write(f"Total Users: {stats['total_users']}")
        st.write(f"Members: {stats['total_members']}")
        st.write(f"Staff: {stats['total_staff']}")
        st.write(f"Active Loans: {stats['active_loans']}")
        st.write(f"Overdue Loans: {stats['overdue_loans']}")


def render_popular_items_report():
    """Render popular items report."""
    library = st.session_state.library_system
    
    st.write("**Most Popular Items Report**")
    
    popular_items = library.get_popular_items(20)
    
    if popular_items:
        popular_data = []
        for i, (item, count) in enumerate(popular_items, 1):
            popular_data.append({
                "Rank": i,
                "Title": item.title,
                "Type": item.get_item_type(),
                "Total Loans": count,
                "Status": "Available" if item.is_available else "Checked Out"
            })
        
        df = pd.DataFrame(popular_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No loan data available for analysis.")


def render_user_activity_report():
    """Render user activity report."""
    library = st.session_state.library_system
    
    st.write("**User Activity Report**")
    
    # Get member activity statistics
    members = library.get_users_by_role('Member')
    
    if members:
        activity_data = []
        for member in members:
            all_loans = library.get_user_loans(member.user_id, active_only=False)
            active_loans = library.get_user_loans(member.user_id, active_only=True)
            
            activity_data.append({
                "Name": member.name,
                "Total Loans": len(all_loans),
                "Active Loans": len(active_loans),
                "Fines Owed": f"${member.fines_owed:.2f}",
                "Status": "Active" if member.is_membership_active() else "Expired"
            })
        
        df = pd.DataFrame(activity_data)
        st.dataframe(df, use_container_width=True)
        
        # Summary statistics
        total_loans = sum(len(library.get_user_loans(m.user_id, active_only=False)) for m in members)
        active_members = len([m for m in members if m.is_membership_active()])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Member Loans", total_loans)
        with col2:
            st.metric("Active Members", active_members)


def render_financial_report():
    """Render financial report."""
    library = st.session_state.library_system
    
    st.write("**Financial Report**")
    
    # Get all loans to calculate financial data
    all_loans = []
    for user in library.get_all_users():
        user_loans = library.get_user_loans(user.user_id, active_only=False)
        all_loans.extend(user_loans)
    
    if all_loans:
        # Calculate financial metrics
        total_fines = sum(loan.fine_amount for loan in all_loans if loan.fine_amount > 0)
        current_fines = sum(loan.fine_amount for loan in all_loans if not loan.is_returned and loan.fine_amount > 0)
        paid_fines = total_fines - current_fines
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Fines Generated", f"${total_fines:.2f}")
        
        with col2:
            st.metric("Outstanding Fines", f"${current_fines:.2f}")
        
        with col3:
            st.metric("Collected Fines", f"${paid_fines:.2f}")
        
        # Fine details
        overdue_loans = library.get_overdue_loans()
        if overdue_loans:
            st.subheader("Current Outstanding Fines")
            
            fine_data = []
            for loan in overdue_loans:
                user = library.get_user(loan.user_id)
                item = library.get_item(loan.item_id)
                
                if user and item and loan.fine_amount > 0:
                    fine_data.append({
                        "User": user.name,
                        "Item": item.title,
                        "Days Overdue": loan.days_overdue(),
                        "Fine Amount": f"${loan.fine_amount:.2f}"
                    })
            
            if fine_data:
                df = pd.DataFrame(fine_data)
                st.dataframe(df, use_container_width=True)


def render_inventory_status_report():
    """Render inventory status report."""
    library = st.session_state.library_system
    
    st.write("**Inventory Status Report**")
    
    # Get inventory statistics
    all_items = library.get_all_items()
    
    if all_items:
        # Calculate statistics by type
        books = [item for item in all_items if item.get_item_type() == "Book"]
        magazines = [item for item in all_items if item.get_item_type() == "Magazine"]
        dvds = [item for item in all_items if item.get_item_type() == "DVD"]
        
        available_books = [item for item in books if item.is_available]
        available_magazines = [item for item in magazines if item.is_available]
        available_dvds = [item for item in dvds if item.is_available]
        
        # Summary table
        inventory_data = [
            {
                "Type": "Books",
                "Total": len(books),
                "Available": len(available_books),
                "Checked Out": len(books) - len(available_books),
                "Availability Rate": f"{(len(available_books)/len(books)*100):.1f}%" if books else "0%"
            },
            {
                "Type": "Magazines",
                "Total": len(magazines),
                "Available": len(available_magazines),
                "Checked Out": len(magazines) - len(available_magazines),
                "Availability Rate": f"{(len(available_magazines)/len(magazines)*100):.1f}%" if magazines else "0%"
            },
            {
                "Type": "DVDs",
                "Total": len(dvds),
                "Available": len(available_dvds),
                "Checked Out": len(dvds) - len(available_dvds),
                "Availability Rate": f"{(len(available_dvds)/len(dvds)*100):.1f}%" if dvds else "0%"
            }
        ]
        
        df = pd.DataFrame(inventory_data)
        st.dataframe(df, use_container_width=True)


def render_system_settings():
    """Render system settings interface."""
    st.subheader("System Settings")
    
    staff = st.session_state.user
    
    if not staff.has_permission("system_admin"):
        st.error("You do not have permission to access system settings.")
        return
    
    # Settings tabs
    tab1, tab2, tab3 = st.tabs(["Loan Settings", "Fine Settings", "System Info"])
    
    with tab1:
        st.write("**Loan Period Settings**")
        st.info("Loan periods are currently hardcoded in the item classes. In a production system, these would be configurable.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("Books: 21 days")
        with col2:
            st.write("Magazines: 7 days")
        with col3:
            st.write("DVDs: 14 days")
    
    with tab2:
        st.write("**Fine Rate Settings**")
        
        current_rate = Loan.get_daily_fine_rate()
        new_rate = st.number_input("Daily Fine Rate ($)", value=current_rate, min_value=0.0, step=0.25)
        
        if st.button("Update Fine Rate"):
            Loan.set_daily_fine_rate(new_rate)
            st.success(f"Fine rate updated to ${new_rate:.2f} per day")
    
    with tab3:
        st.write("**System Information**")
        library = st.session_state.library_system
        stats = library.get_system_statistics()
        
        st.write(f"Library Name: {stats['library_name']}")
        st.write(f"System Uptime: {stats['system_uptime_days']} days")
        st.write(f"Database: SQLite")
        st.write(f"Version: 1.0.0")


# Helper functions
def add_new_item(item_type: str, item_id: str, title: str, form_data: dict) -> bool:
    """Add a new item to the library."""
    try:
        library = st.session_state.library_system
        db_manager = st.session_state.db_manager
        
        if item_type == "Book":
            item = Book(
                item_id=item_id,
                title=title,
                author=form_data['author'],
                isbn=form_data.get('isbn', ''),
                pages=form_data.get('pages', 0)
            )
        elif item_type == "Magazine":
            item = Magazine(
                item_id=item_id,
                title=title,
                issue_number=form_data['issue_number'],
                publisher=form_data['publisher'],
                publication_date=form_data['pub_date']
            )
        elif item_type == "DVD":
            item = DVD(
                item_id=item_id,
                title=title,
                duration=form_data['duration'],
                genre=form_data['genre'],
                director=form_data.get('director'),
                rating=form_data.get('rating')
            )
        else:
            return False
        
        # Add to library system
        if library.add_item(item):
            # Save to database
            db_manager.save_item(item)
            return True
        else:
            st.error("Item ID already exists.")
            return False
    
    except Exception as e:
        st.error(f"Error adding item: {e}")
        return False


def remove_item(item_id: str) -> bool:
    """Remove an item from the library."""
    try:
        library = st.session_state.library_system
        db_manager = st.session_state.db_manager
        
        if library.remove_item(item_id):
            db_manager.delete_item(item_id)
            return True
        else:
            st.error("Cannot remove item - it may be currently borrowed or not found.")
            return False
    
    except Exception as e:
        st.error(f"Error removing item: {e}")
        return False


def register_new_user(user_type: str, user_id: str, name: str, email: str, form_data: dict) -> bool:
    """Register a new user."""
    try:
        library = st.session_state.library_system
        db_manager = st.session_state.db_manager
        
        if user_type == "Member":
            user = Member(
                user_id=user_id,
                name=name,
                email=email,
                phone=form_data.get('phone')
            )
        elif user_type == "Staff":
            user = Staff(
                user_id=user_id,
                name=name,
                email=email,
                role=form_data['staff_role'],
                hire_date=form_data['hire_date']
            )
        else:
            return False
        
        # Register in library system
        if library.register_user(user):
            # Save to database
            db_manager.save_user(user)
            return True
        else:
            st.error("User ID already exists.")
            return False
    
    except Exception as e:
        st.error(f"Error registering user: {e}")
        return False 