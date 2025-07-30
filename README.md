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

### Object-Oriented Programming Concepts Demonstrated

- **Abstract Classes**: `LibraryItem` and `User` base classes with abstract methods
- **Inheritance**: Item types (`Book`, `Magazine`, `DVD`) and user types (`Member`, `Staff`)
- **Polymorphism**: Method overriding for different behaviors (loan periods, borrowing limits)
- **Encapsulation**: Protected attributes with property decorators and validation
- **Static Attributes/Methods**: Class-level counters and utility functions
- **Composition**: `LibrarySystem` managing collections of other objects

## Technology Stack

- **Backend**: Python 3.8+
- **Frontend**: Streamlit
- **Database**: SQLite
- **Testing**: pytest
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
├── scripts/
│   ├── seed_database.py          # Database seeding script
│   └── test_system.py            # Comprehensive test suite
├── assets/
│   └── uml_library_management.png # UML class diagram
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
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

4. **Initialise the database with sample data**:
   ```bash
   python scripts/seed_database.py
   ```

5. **Run the test suite** (optional):
   ```bash
   python scripts/test_system.py
   ```

## Running the Application

### Web Interface (Recommended)

1. **Start the Streamlit application**:
   ```bash
   streamlit run src/frontend/app.py
   ```

2. **Access the application** in your web browser at `http://localhost:8501`

3. **Login using demo credentials**:

   **Member Accounts**:
   - `M001` - Alice Johnson
   - `M002` - Bob Smith
   - `M003` - Carol Davis
   - `M004` - David Wilson
   - `M005` - Emma Brown

   **Staff Accounts**:
   - `S001` - Sarah Williams (Manager)
   - `S002` - Michael Rodriguez (Librarian)
   - `S003` - Jennifer Martinez (Librarian)
   - `S004` - Robert Thompson (Manager)
   - `S005` - Lisa Garcia (Librarian)

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

## Testing

The project includes a comprehensive test suite that validates all OOP principles:

```bash
python scripts/test_system.py
```

**Test Coverage**:
- Abstract class instantiation prevention
- Inheritance and polymorphism verification
- Encapsulation and property validation
- Static attributes and methods
- Business logic functionality
- Error handling and validation

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

## Assignment Requirements Fulfillment

- **UML Diagram**: Complete class diagram showing relationships
- **Abstract Classes**: `LibraryItem` and `User` with abstract methods
- **Inheritance**: Multiple levels with `Book`/`Magazine`/`DVD` and `Member`/`Staff`
- **Polymorphism**: Method overriding for type-specific behavior
- **Encapsulation**: Protected attributes with property access
- **Static Elements**: Class counters and utility methods
- **Clean Code**: Comprehensive documentation and type hints
- **Error Handling**: Validation and graceful error management

### Key Design Decisions

1. **Layered Architecture**: Separation of models, database, and presentation layers
2. **Abstract Base Classes**: Enforce contracts and enable polymorphism
3. **Property Decorators**: Provide controlled access to internal state
4. **Static Methods**: Track system-wide statistics and configurations

