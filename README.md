# Library Management System

A library management system demonstrating object-oriented programming principles for Programming Design Paradigm MSc coursework.

## Project Overview

This project implements a library management system with a focus on demonstrating key OOP concepts including inheritance, polymorphism, encapsulation, and abstract classes. The system manages both physical and digital media with separate interfaces for library members and staff.

## Features

### Core Functionality
- **Item Management**: Books, Magazines, and DVDs with type-specific attributes
- **User Management**: Members and Staff with role-based permissions
- **Loan System**: Check-out, check-in, renewals, and fine calculation
- **Database Persistence**: SQLite database with full CRUD operations
- **Web Interface**: Streamlit-based frontend with separate Member and Staff views

### OOP Concepts Used

- **Abstract Classes**: Base classes that enforce method implementation in subclasses
- **Inheritance**: Different item types and user types inherit common functionality  
- **Polymorphism**: Same method names behave differently (e.g., loan periods vary by item type)
- **Encapsulation**: Private attributes with controlled access via properties
- **Static Methods**: Class-level counters and utility functions
- **Composition**: Main system coordinates multiple object types

## Technology Stack

- **Backend**: Python 3.10+
- **Frontend**: Streamlit
- **Database**: SQLite
- **Architecture**: Layered architecture with models, database, and frontend layers

## Project Structure

```
AE1-library-management/
├── src/
│   ├── models/
│   │   ├── abstract_classes.py    # Abstract base classes
│   │   ├── items.py              # LibraryItem implementations
│   │   ├── users.py              # User implementations
│   │   ├── loan.py               # Loan transaction class
│   │   └── library_system.py    # Main system controller
│   ├── database/
│   │   ├── schema.py             # Database schema definition
│   │   └── database_manager.py   # Database operations
│   └── frontend/
│       ├── app.py                # Main Streamlit application
│       ├── member_interface.py   # Member UI components
│       └── staff_interface.py    # Staff UI components
├── requirements.txt              # Python dependencies
└── README.md                     # This file!
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. **Clone or extract the project**:
   ```bash
   cd AE1-library-management
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialise the database with sample data if not already**:
   ```bash
   python scripts/seed_database.py
   ```


## Running the Application

### Web Interface

1. **Start the Streamlit application**:
   ```bash
   streamlit run src/frontend/app.py
   ```

2. **Access the application** in your web browser at `http://localhost:8501`

3. **Login using demo credentials**:

   **Member Accounts**:
   - `M001` - Marcelo Amorelli
   - `M002` - Umar Hussain

   **Staff Accounts**:
   - `S001` - Jiri Motejlek (Manager)

### Command Line Interface

You can also interact with the system programmatically:

```python
# Example usage
from src.models.library_system import LibrarySystem
from src.database.database_manager import DatabaseManager

# Initialise system
library = LibrarySystem("My Library")
db_manager = DatabaseManager("library.db")

# Load data from database
users = db_manager.get_all_users()
items = db_manager.get_all_items()

for user in users:
    library.register_user(user)
for item in items:
    library.add_item(item)

# Check out an item
success, message = library.check_out_item("M001", "B001")
print(f"Checkout result: {message}")
```

## User Guide

### For Members

1. **Dashboard**: View your current loans, due dates, and account status
2. **Browse Items**: Explore the library catalog with filtering and sorting options
3. **Search**: Find specific items by title
4. **My Loans**: Manage current loans (return/renew) and view loan history
5. **Account**: View personal information and membership details

### For Staff

1. **Dashboard**: System overview with key metrics and alerts
2. **Manage Items**: Add, edit, or remove library items
3. **Manage Users**: Register new users and view user details
4. **Loan Management**: View active loans, overdue items, and loan history
5. **Reports**: Generate system reports and analytics
6. **Settings**: Configure system parameters (for authorised staff)

## Database Schema

The system uses SQLite with the following main tables:

- **users**: User information with role-specific fields
- **items**: Library items with type-specific metadata
- **loans**: Loan transactions and history
- **system_info**: System configuration and metadata

## Object-Oriented Design Patterns

### Abstract Factory Pattern
- `LibraryItem` and `User` abstract classes define interfaces
- Concrete implementations provide specific behaviors

### Composition Pattern
- `LibrarySystem` composes and coordinates other objects
- Separation of concerns between models, database, and presentation

### Strategy Pattern
- Different borrowing limits and loan periods based on user/item types
- Polymorphic method implementations

## OOP Requirements Met

- **UML Diagram**: Class relationships diagram included
- **Abstract Classes**: Base classes with abstract methods that subclasses must implement
- **Inheritance**: Item types and user types inherit from base classes
- **Polymorphism**: Same method names work differently for different types
- **Encapsulation**: Private data with controlled access through properties
- **Static Elements**: Class-level counters and shared methods
- **Error Handling**: Input validation and proper error messages

### Design Notes

- **Layered Architecture**: Models, database, and frontend are separated
- **Abstract Classes**: Force subclasses to implement required methods
- **Properties**: Control access to internal data
- **Static Methods**: Track counters and system stats


Happy Reading!

