# Simple RDBMS with Task Management Web App

A complete implementation of a simple Relational Database Management System (RDBMS) from scratch, with a demonstration web application for task management.

## Features

### RDBMS Core Features
- **Multiple Data Types**: INTEGER, VARCHAR, FLOAT, BOOLEAN, DATE
- **Table Operations**: CREATE TABLE, DROP TABLE, DESCRIBE
- **CRUD Operations**: INSERT, SELECT, UPDATE, DELETE
- **Constraints**: PRIMARY KEY, UNIQUE, NOT NULL
- **Indexing**: Automatic indexing for primary and unique keys, manual index creation
- **JOIN Operations**: INNER JOIN and LEFT JOIN support
- **SQL Parser**: Parse and execute SQL statements
- **Interactive REPL**: Command-line interface for database interaction
- **Persistence**: Save and load database state from JSON files

### Web Application Features
- **User Management**: Create, read, update, and delete users
- **Project Management**: Organize tasks into projects
- **Task Management**: Full CRUD operations on tasks with status tracking
- **SQL Console**: Execute raw SQL queries through the web interface
- **Responsive Design**: Mobile-friendly UI

## Project Structure

```
.
├── rdbms/                  # Core RDBMS implementation
│   ├── __init__.py
│   ├── data_types.py      # Data type definitions
│   ├── table.py           # Table and column implementation
│   ├── index.py           # Indexing system
│   ├── database.py        # Database management
│   ├── sql_parser.py      # SQL parser and executor
│   └── repl.py            # Interactive REPL
├── webapp/                 # Web application
│   ├── app.py             # Flask application
│   ├── templates/         # HTML templates
│   └── static/            # CSS and assets
├── tests/                  # Test suite
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/REVOgati/gareth_JDEV26_Project.git
cd gareth_JDEV26_Project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Interactive REPL Mode

Start the interactive SQL shell:

```bash
python -m rdbms.repl
```

Example commands:

```sql
-- Create a table
CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(50), email VARCHAR(100) UNIQUE);

-- Insert data
INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com');

-- Query data
SELECT * FROM users;

-- Update data
UPDATE users SET name = 'Alice Smith' WHERE id = 1;

-- Delete data
DELETE FROM users WHERE id = 1;

-- Create an index
CREATE INDEX idx_email ON users (email);

-- Join tables
SELECT * FROM tasks JOIN projects ON tasks.project_id = projects.id;
```

Special commands:
- `help` - Show available commands
- `tables` - List all tables
- `describe <table>` - Show table structure
- `exit` or `quit` - Exit the REPL

### Web Application

Start the web application:

```bash
cd webapp
python app.py
```

The application will be available at `http://localhost:5000`

Features:
- **Home**: Overview dashboard with statistics
- **Users**: Manage user accounts
- **Projects**: Create and organize projects
- **Tasks**: Track tasks with priorities, status, and assignments
- **SQL Console**: Execute raw SQL queries

## Architecture

### Data Storage Layer
The RDBMS uses an in-memory storage model with optional JSON persistence:
- **Tables**: Store rows as dictionaries
- **Indexes**: Hash-based indexes for fast lookups
- **Constraints**: Validated on insert/update operations

### SQL Parser
A simple recursive descent parser that supports:
- DDL: CREATE TABLE, DROP TABLE, CREATE INDEX
- DML: INSERT, SELECT, UPDATE, DELETE
- WHERE clauses with comparison operators
- JOIN operations (INNER and LEFT)

### Web Application
Built with Flask, demonstrating real-world CRUD operations:
- **Users Table**: User account management
- **Projects Table**: Project organization with ownership
- **Tasks Table**: Task tracking with foreign keys to projects and users

## Example Use Case: Task Management

The included web application demonstrates a practical task management system:

1. **Users** represent team members
2. **Projects** organize work with an owner
3. **Tasks** belong to projects and can be assigned to users
4. Tasks track: title, description, status, priority, due date, completion

The system demonstrates:
- Foreign key relationships (without enforcement)
- JOINs to display related data
- Complex queries with filters
- Full CRUD operations through a web UI

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

## Supported SQL Syntax

### CREATE TABLE
```sql
CREATE TABLE table_name (
    col1 INTEGER PRIMARY KEY,
    col2 VARCHAR(50) NOT NULL,
    col3 DATE,
    col4 BOOLEAN
);
```

### INSERT
```sql
INSERT INTO table_name (col1, col2) VALUES (val1, val2);
```

### SELECT
```sql
SELECT col1, col2 FROM table_name WHERE col1 = value;
SELECT * FROM table1 JOIN table2 ON table1.id = table2.fk_id;
SELECT * FROM table1 LEFT JOIN table2 ON table1.id = table2.fk_id;
```

### UPDATE
```sql
UPDATE table_name SET col1 = val1, col2 = val2 WHERE condition;
```

### DELETE
```sql
DELETE FROM table_name WHERE condition;
```

### CREATE INDEX
```sql
CREATE INDEX idx_name ON table_name (column_name);
CREATE UNIQUE INDEX idx_name ON table_name (column_name);
```

## Limitations

This is a simple medium-level RDBMS practice project with the following limitations:
- In-memory storage (with JSON persistence)
- No transaction support
- No concurrent access handling
- Limited query optimization
- Simple WHERE clause parsing (single condition only)
- No foreign key constraints
- No aggregate functions (COUNT, SUM, etc.)
- No GROUP BY or ORDER BY

## Future Enhancements

Potential improvements:
- Transaction support with ACID properties
- Query optimization and execution plans
- Multi-threaded access with locking
- More complex WHERE clauses (AND, OR, NOT)
- Aggregate functions and GROUP BY
- Foreign key constraints with cascade
- B-tree indexes for range queries
- Query caching

## License

MIT License - feel free to use this for educational purposes.

## Author

Gareth - JDEV26 Project

## Acknowledgments

This project demonstrates fundamental database concepts including:
- Data structures for storage (hash tables, indexes)
- SQL parsing and execution
- Constraint enforcement
- Join algorithms
- Web application integration
