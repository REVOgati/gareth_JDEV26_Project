#!/usr/bin/env python3
"""
Demo script for the RDBMS system.
This script demonstrates all major features of the RDBMS.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rdbms import Database, Column, Integer, VarChar, Date, Boolean, Float, SQLParser
from datetime import date


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_results(results):
    """Pretty print query results."""
    if not results:
        print("  (0 rows)")
        return
    
    # Get column names
    columns = list(results[0].keys())
    
    # Calculate column widths
    widths = {col: len(col) for col in columns}
    for row in results:
        for col in columns:
            val = str(row[col]) if row[col] is not None else "NULL"
            widths[col] = max(widths[col], len(val))
    
    # Print header
    header = " | ".join(col.ljust(widths[col]) for col in columns)
    print("\n  " + header)
    print("  " + "-" * len(header))
    
    # Print rows
    for row in results:
        values = []
        for col in columns:
            val = str(row[col]) if row[col] is not None else "NULL"
            values.append(val.ljust(widths[col]))
        print("  " + " | ".join(values))
    
    print(f"\n  ({len(results)} row{'s' if len(results) != 1 else ''})")


def main():
    """Run the demo."""
    print("\n" + "=" * 70)
    print("  Simple RDBMS - Feature Demonstration")
    print("=" * 70)
    
    # Create database
    print_section("1. Creating Database")
    db = Database('demo')
    print("  ✓ Database 'demo' created")
    
    # Create tables using SQL
    print_section("2. Creating Tables with SQL")
    parser = SQLParser(db)
    
    parser.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE,
            department VARCHAR(50),
            salary FLOAT,
            hire_date DATE
        )
    """)
    print("  ✓ Table 'employees' created")
    
    parser.execute("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            budget FLOAT
        )
    """)
    print("  ✓ Table 'departments' created")
    
    # Insert data
    print_section("3. Inserting Data")
    
    parser.execute("INSERT INTO departments (id, name, budget) VALUES (1, 'Engineering', 500000.0)")
    parser.execute("INSERT INTO departments (id, name, budget) VALUES (2, 'Marketing', 300000.0)")
    parser.execute("INSERT INTO departments (id, name, budget) VALUES (3, 'Sales', 400000.0)")
    print("  ✓ 3 departments inserted")
    
    parser.execute("INSERT INTO employees (id, name, email, department, salary, hire_date) VALUES (1, 'Alice Smith', 'alice@company.com', 'Engineering', 95000.0, '2024-01-15')")
    parser.execute("INSERT INTO employees (id, name, email, department, salary, hire_date) VALUES (2, 'Bob Jones', 'bob@company.com', 'Engineering', 85000.0, '2024-03-20')")
    parser.execute("INSERT INTO employees (id, name, email, department, salary, hire_date) VALUES (3, 'Carol White', 'carol@company.com', 'Marketing', 75000.0, '2024-02-10')")
    parser.execute("INSERT INTO employees (id, name, email, department, salary, hire_date) VALUES (4, 'David Brown', 'david@company.com', 'Sales', 80000.0, '2023-11-05')")
    print("  ✓ 4 employees inserted")
    
    # SELECT queries
    print_section("4. SELECT Queries")
    print("\n  Query: SELECT * FROM employees")
    results = parser.execute("SELECT * FROM employees")
    print_results(results)
    
    print("\n  Query: SELECT name, department, salary FROM employees WHERE salary > 80000")
    results = parser.execute("SELECT name, department, salary FROM employees WHERE salary > 80000")
    print_results(results)
    
    # JOIN query
    print_section("5. JOIN Operations")
    print("\n  Query: SELECT * FROM employees JOIN departments ON employees.department = departments.name")
    
    # Note: We need to adjust this since our JOIN uses column references
    # Let's create a proper relational structure
    parser.execute("DROP TABLE employees")
    parser.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE,
            dept_id INTEGER,
            salary FLOAT,
            hire_date DATE
        )
    """)
    
    parser.execute("INSERT INTO employees (id, name, email, dept_id, salary, hire_date) VALUES (1, 'Alice Smith', 'alice@company.com', 1, 95000.0, '2024-01-15')")
    parser.execute("INSERT INTO employees (id, name, email, dept_id, salary, hire_date) VALUES (2, 'Bob Jones', 'bob@company.com', 1, 85000.0, '2024-03-20')")
    parser.execute("INSERT INTO employees (id, name, email, dept_id, salary, hire_date) VALUES (3, 'Carol White', 'carol@company.com', 2, 75000.0, '2024-02-10')")
    parser.execute("INSERT INTO employees (id, name, email, dept_id, salary, hire_date) VALUES (4, 'David Brown', 'david@company.com', 3, 80000.0, '2023-11-05')")
    
    results = parser.execute("SELECT employees.name, departments.name, employees.salary FROM employees JOIN departments ON employees.dept_id = departments.id")
    print_results(results)
    
    # UPDATE
    print_section("6. UPDATE Operations")
    print("\n  Query: UPDATE employees SET salary = 100000.0 WHERE id = 1")
    result = parser.execute("UPDATE employees SET salary = 100000.0 WHERE id = 1")
    print(f"  {result}")
    
    print("\n  Verifying update...")
    results = parser.execute("SELECT name, salary FROM employees WHERE id = 1")
    print_results(results)
    
    # DELETE
    print_section("7. DELETE Operations")
    print("\n  Query: DELETE FROM employees WHERE id = 4")
    result = parser.execute("DELETE FROM employees WHERE id = 4")
    print(f"  {result}")
    
    print("\n  Remaining employees:")
    results = parser.execute("SELECT name FROM employees")
    print_results(results)
    
    # Constraints demonstration
    print_section("8. Constraint Enforcement")
    print("\n  Attempting to insert duplicate primary key...")
    try:
        parser.execute("INSERT INTO employees (id, name, email, dept_id, salary, hire_date) VALUES (1, 'Test User', 'test@company.com', 1, 50000.0, '2024-01-01')")
    except ValueError as e:
        print(f"  ✓ Error caught: {e}")
    
    print("\n  Attempting to insert duplicate unique email...")
    try:
        parser.execute("INSERT INTO employees (id, name, email, dept_id, salary, hire_date) VALUES (10, 'Another User', 'alice@company.com', 1, 50000.0, '2024-01-01')")
    except ValueError as e:
        print(f"  ✓ Error caught: {e}")
    
    # Indexing
    print_section("9. Index Operations")
    print("\n  Creating index on salary column...")
    parser.execute("CREATE INDEX idx_salary ON employees (salary)")
    print("  ✓ Index created")
    
    employees_table = db.get_table('employees')
    print(f"  Indexes on employees table: {list(employees_table.indexes.keys())}")
    
    # Persistence
    print_section("10. Database Persistence")
    print("\n  Saving database to file...")
    db.save('/tmp/demo.db.json')
    print("  ✓ Database saved to /tmp/demo.db.json")
    
    print("\n  Loading database from file...")
    db2 = Database.load('/tmp/demo.db.json')
    print("  ✓ Database loaded")
    
    print("\n  Verifying data after load...")
    parser2 = SQLParser(db2)
    results = parser2.execute("SELECT name, salary FROM employees")
    print_results(results)
    
    # Summary
    print_section("Demo Complete!")
    print("""
  This demo showcased:
    ✓ Database and table creation
    ✓ Multiple data types (INTEGER, VARCHAR, FLOAT, DATE)
    ✓ SQL parsing and execution
    ✓ CRUD operations (Create, Read, Update, Delete)
    ✓ JOIN operations (INNER JOIN)
    ✓ Constraints (PRIMARY KEY, UNIQUE, NOT NULL)
    ✓ Indexing for performance
    ✓ Data persistence (save/load from JSON)
    
  For more features, try:
    - The interactive REPL: python -m rdbms.repl
    - The web application: cd webapp && python app.py
    """)
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
