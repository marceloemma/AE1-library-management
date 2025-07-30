"""
Database layer for the Library Management System.

This module provides SQLite database functionality for persisting
library data including users, items, and loans.
"""

from .database_manager import DatabaseManager
from .schema import create_tables, get_schema_version

__all__ = ['DatabaseManager', 'create_tables', 'get_schema_version'] 