"""
Member interface for the Library Management System.

This module provides the Streamlit interface for library members to browse items,
manage loans, and view their account information.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List
from models.items import Book, Magazine, DVD
from models.users import Member


def render_member_interface():
    """Render the main member interface."""
    member = st.session_state.user
    library = st.session_state.library_system
    db_manager = st.session_state.db_manager
    
    # Sidebar navigation
    st.sidebar.title("Member Menu")
    
    menu_options = [
        "Dashboard",
        "Browse Items", 
        "My Loans",
        "Search Items",
        "Account Information"
    ]
    
    selected_page = st.sidebar.radio("Navigate to:", menu_options)
    
    # Display current borrowing status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quick Stats")
    borrowed_items = len(member.borrowed_items)
    borrowing_limit = member.get_borrowing_limit()
    
    st.sidebar.metric("Items Borrowed", f"{borrowed_items}/{borrowing_limit}")
    
    if member.fines_owed > 0:
        st.sidebar.error(f"Outstanding Fines: ${member.fines_owed:.2f}")
    else:
        st.sidebar.success("No outstanding fines")
    
    # Render selected page
    if selected_page == "Dashboard":
        render_member_dashboard()
    elif selected_page == "Browse Items":
        render_browse_items()
    elif selected_page == "My Loans":
        render_my_loans()
    elif selected_page == "Search Items":
        render_search_items()
    elif selected_page == "Account Information":
        render_account_info()


def render_member_dashboard():
    """Render the member dashboard."""
    st.subheader("Member Dashboard")
    
    member = st.session_state.user
    library = st.session_state.library_system
    
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Items Borrowed", len(member.borrowed_items))
    
    with col2:
        st.metric("Borrowing Limit", member.get_borrowing_limit())
    
    with col3:
        st.metric("Outstanding Fines", f"${member.fines_owed:.2f}")
    
    with col4:
        membership_status = "Active" if member.is_membership_active() else "Expired"
        st.metric("Membership", membership_status)
    
    # Current loans
    st.subheader("Current Loans")
    active_loans = library.get_user_loans(member.user_id, active_only=True)
    
    if active_loans:
        loans_data = []
        for loan in active_loans:
            item = library.get_item(loan.item_id)
            if item:
                status = "Overdue" if loan.is_overdue() else "Active"
                days_remaining = (loan.date_due - datetime.now()).days
                
                loans_data.append({
                    "Title": item.title,
                    "Type": item.get_item_type(),
                    "Due Date": loan.date_due.strftime("%Y-%m-%d"),
                    "Days Remaining": days_remaining,
                    "Status": status,
                    "Fine": f"${loan.fine_amount:.2f}" if loan.fine_amount > 0 else "None"
                })
        
        df = pd.DataFrame(loans_data)
        st.dataframe(df, use_container_width=True)
        
        # Show overdue warnings
        overdue_loans = [loan for loan in active_loans if loan.is_overdue()]
        if overdue_loans:
            st.warning(f"You have {len(overdue_loans)} overdue item(s). Please return them to avoid additional fines.")
    else:
        st.info("You have no current loans.")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Browse New Items", use_container_width=True):
            st.session_state.selected_page = "Browse Items"
            st.rerun()
    
    with col2:
        if st.button("View Account Details", use_container_width=True):
            st.session_state.selected_page = "Account Information"
            st.rerun()


def render_browse_items():
    """Render the item browsing interface."""
    st.subheader("Browse Library Items")
    
    library = st.session_state.library_system
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        item_type_filter = st.selectbox(
            "Filter by Type",
            ["All", "Book", "Magazine", "DVD"]
        )
    
    with col2:
        availability_filter = st.selectbox(
            "Availability",
            ["All", "Available", "Checked Out"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Title", "Type", "Date Added"]
        )
    
    # Get and filter items
    all_items = library.get_all_items()
    filtered_items = []
    
    for item in all_items:
        # Apply type filter
        if item_type_filter != "All" and item.get_item_type() != item_type_filter:
            continue
        
        # Apply availability filter
        if availability_filter == "Available" and not item.is_available:
            continue
        elif availability_filter == "Checked Out" and item.is_available:
            continue
        
        filtered_items.append(item)
    
    # Sort items
    if sort_by == "Title":
        filtered_items.sort(key=lambda x: x.title)
    elif sort_by == "Type":
        filtered_items.sort(key=lambda x: x.get_item_type())
    elif sort_by == "Date Added":
        filtered_items.sort(key=lambda x: x.date_added, reverse=True)
    
    st.write(f"Showing {len(filtered_items)} items")
    
    # Display items
    for item in filtered_items:
        with st.expander(f"{item.get_item_type()}: {item.title}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Title:** {item.title}")
                
                if isinstance(item, Book):
                    st.write(f"**Author:** {item.author}")
                    st.write(f"**ISBN:** {item.isbn}")
                    if item.pages > 0:
                        st.write(f"**Pages:** {item.pages}")
                
                elif isinstance(item, Magazine):
                    st.write(f"**Publisher:** {item.publisher}")
                    st.write(f"**Issue:** {item.issue_number}")
                    st.write(f"**Publication Date:** {item.publication_date.strftime('%Y-%m-%d')}")
                
                elif isinstance(item, DVD):
                    st.write(f"**Duration:** {item.get_formatted_duration()}")
                    st.write(f"**Genre:** {item.genre}")
                    if item.director:
                        st.write(f"**Director:** {item.director}")
                    if item.rating:
                        st.write(f"**Rating:** {item.rating}")
                
                st.write(f"**Loan Period:** {item.get_loan_period()} days")
                st.write(f"**Date Added:** {item.date_added.strftime('%Y-%m-%d')}")
            
            with col2:
                if item.is_available:
                    st.success("Available")
                    if st.button(f"Borrow", key=f"borrow_{item.item_id}"):
                        borrow_item(item.item_id)
                else:
                    st.error("Checked Out")


def render_my_loans():
    """Render the user's loan history and current loans."""
    st.subheader("My Loans")
    
    member = st.session_state.user
    library = st.session_state.library_system
    
    # Tabs for current and historical loans
    tab1, tab2 = st.tabs(["Current Loans", "Loan History"])
    
    with tab1:
        active_loans = library.get_user_loans(member.user_id, active_only=True)
        
        if active_loans:
            for loan in active_loans:
                item = library.get_item(loan.item_id)
                if item:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"**{item.title}** ({item.get_item_type()})")
                            st.write(f"Borrowed: {loan.date_borrowed.strftime('%Y-%m-%d')}")
                            st.write(f"Due: {loan.date_due.strftime('%Y-%m-%d')}")
                        
                        with col2:
                            if loan.is_overdue():
                                st.error(f"Overdue by {loan.days_overdue()} days")
                                st.write(f"Fine: ${loan.fine_amount:.2f}")
                            else:
                                days_left = (loan.date_due - datetime.now()).days
                                st.info(f"{days_left} days remaining")
                        
                        with col3:
                            if st.button("Return", key=f"return_{loan.loan_id}"):
                                return_item(loan.item_id)
                            
                            if loan.can_renew() and st.button("Renew", key=f"renew_{loan.loan_id}"):
                                renew_loan(loan.item_id)
                        
                        st.markdown("---")
        else:
            st.info("You have no current loans.")
    
    with tab2:
        all_loans = library.get_user_loans(member.user_id, active_only=False)
        historical_loans = [loan for loan in all_loans if loan.is_returned]
        
        if historical_loans:
            loans_data = []
            for loan in historical_loans:
                item = library.get_item(loan.item_id)
                if item:
                    loans_data.append({
                        "Title": item.title,
                        "Type": item.get_item_type(),
                        "Borrowed": loan.date_borrowed.strftime("%Y-%m-%d"),
                        "Returned": loan.date_returned.strftime("%Y-%m-%d") if loan.date_returned else "N/A",
                        "Duration": loan.get_loan_duration(),
                        "Fine": f"${loan.fine_amount:.2f}" if loan.fine_amount > 0 else "None"
                    })
            
            df = pd.DataFrame(loans_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No loan history available.")


def render_search_items():
    """Render the item search interface."""
    st.subheader("Search Library Items")
    
    # Search input
    search_query = st.text_input("Search by title:", placeholder="Enter book title, magazine name, or movie title...")
    
    if search_query:
        library = st.session_state.library_system
        results = library.search_items(search_query)
        
        if results:
            st.write(f"Found {len(results)} results for '{search_query}':")
            
            for item in results:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**{item.title}** ({item.get_item_type()})")
                        
                        if isinstance(item, Book):
                            st.write(f"by {item.author}")
                        elif isinstance(item, Magazine):
                            st.write(f"Published by {item.publisher}")
                        elif isinstance(item, DVD):
                            if item.director:
                                st.write(f"Directed by {item.director}")
                    
                    with col2:
                        if item.is_available:
                            st.success("Available")
                            if st.button("Borrow", key=f"search_borrow_{item.item_id}"):
                                borrow_item(item.item_id)
                        else:
                            st.error("Checked Out")
                    
                    st.markdown("---")
        else:
            st.warning(f"No items found matching '{search_query}'.")


def render_account_info():
    """Render the account information page."""
    st.subheader("Account Information")
    
    member = st.session_state.user
    
    # Account details
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Personal Information**")
        st.write(f"Name: {member.name}")
        st.write(f"Email: {member.email}")
        st.write(f"Phone: {member.phone or 'Not provided'}")
        st.write(f"User ID: {member.user_id}")
    
    with col2:
        st.write("**Membership Details**")
        st.write(f"Borrowing Limit: {member.get_borrowing_limit()} items")
        st.write(f"Registration Date: {member.registration_date.strftime('%Y-%m-%d')}")
        
        membership_status = "Active" if member.is_membership_active() else "Expired"
        st.write(f"Status: {membership_status}")
        
        if member.is_membership_active():
            st.write(f"Expires: {member.membership_expiry.strftime('%Y-%m-%d')}")
    
    # Financial information
    st.write("**Financial Information**")
    if member.fines_owed > 0:
        st.error(f"Outstanding Fines: ${member.fines_owed:.2f}")
        st.warning("Please pay outstanding fines to maintain borrowing privileges.")
    else:
        st.success("No outstanding fines")
    
    # Account statistics
    library = st.session_state.library_system
    all_loans = library.get_user_loans(member.user_id, active_only=False)
    
    st.write("**Account Statistics**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Loans", len(all_loans))
    
    with col2:
        current_loans = len(member.borrowed_items)
        st.metric("Current Loans", current_loans)
    
    with col3:
        total_fines = sum(loan.fine_amount for loan in all_loans if loan.fine_amount > 0)
        st.metric("Lifetime Fines", f"${total_fines:.2f}")


def borrow_item(item_id: str):
    """Handle item borrowing."""
    member = st.session_state.user
    library = st.session_state.library_system
    db_manager = st.session_state.db_manager
    
    success, message = library.check_out_item(member.user_id, item_id)
    
    if success:
        # Save the loan to database
        user_loans = library.get_user_loans(member.user_id, active_only=True)
        for loan in user_loans:
            if loan.item_id == item_id and not loan.is_returned:
                db_manager.save_loan(loan)
                break
        
        # Update item in database
        item = library.get_item(item_id)
        if item:
            db_manager.save_item(item)
        
        # Update user in database
        db_manager.save_user(member)
        
        st.success(message)
        st.rerun()
    else:
        st.error(message)


def return_item(item_id: str):
    """Handle item return."""
    member = st.session_state.user
    library = st.session_state.library_system
    db_manager = st.session_state.db_manager
    
    success, message, fine = library.check_in_item(member.user_id, item_id)
    
    if success:
        # Update loan in database
        user_loans = library.get_user_loans(member.user_id, active_only=False)
        for loan in user_loans:
            if loan.item_id == item_id and loan.is_returned:
                db_manager.save_loan(loan)
                break
        
        # Update item in database
        item = library.get_item(item_id)
        if item:
            db_manager.save_item(item)
        
        # Update user in database
        db_manager.save_user(member)
        
        if fine > 0:
            st.warning(f"{message}")
        else:
            st.success(message)
        st.rerun()
    else:
        st.error(message)


def renew_loan(item_id: str):
    """Handle loan renewal."""
    member = st.session_state.user
    library = st.session_state.library_system
    db_manager = st.session_state.db_manager
    
    success, message = library.renew_loan(member.user_id, item_id)
    
    if success:
        # Update loan in database
        user_loans = library.get_user_loans(member.user_id, active_only=True)
        for loan in user_loans:
            if loan.item_id == item_id:
                db_manager.save_loan(loan)
                break
        
        st.success(message)
        st.rerun()
    else:
        st.error(message) 