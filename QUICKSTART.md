# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/REVOgati/gareth_JDEV26_Project.git
cd gareth_JDEV26_Project

# Install dependencies
pip install -r requirements.txt
```

## Running the Demo

See all features in action:

```bash
python demo.py
```

## Interactive REPL

Start the SQL shell:

```bash
python -m rdbms.repl
```

Example session:

```sql
sql> CREATE TABLE products (
...>     id INTEGER PRIMARY KEY,
...>     name VARCHAR(100) NOT NULL,
...>     price FLOAT,
...>     in_stock BOOLEAN
...> );
Table products created successfully

sql> INSERT INTO products (id, name, price, in_stock) VALUES (1, 'Laptop', 999.99, TRUE);
1 row inserted (ID: 0)

sql> SELECT * FROM products;
id | name   | price  | in_stock
--------------------------------
1  | Laptop | 999.99 | True    

(1 row)

sql> help
[Shows available commands]

sql> exit
Goodbye!
```

## Web Application

Start the task management web app:

```bash
cd webapp
python app.py
```

Then open your browser to: `http://localhost:5000`

### Web App Features

- **Dashboard** - Overview of users, projects, and tasks
- **Users** - Create and manage user accounts
- **Projects** - Organize work into projects
- **Tasks** - Track tasks with status, priority, assignments
- **SQL Console** - Execute raw SQL queries

## Testing

Run the test suite:

```bash
python run_tests.py
```

All 23 tests should pass.

## Programmatic Usage

Use the RDBMS in your Python code:

```python
from rdbms import Database, Column, Integer, VarChar, Date
from datetime import date

# Create database
db = Database('myapp')

# Create table
table = db.create_table('users', [
    Column('id', Integer(nullable=False), primary_key=True),
    Column('username', VarChar(50, nullable=False), unique=True),
    Column('email', VarChar(100), unique=True),
    Column('created_at', Date())
])

# Insert data
table.insert({
    'id': 1,
    'username': 'alice',
    'email': 'alice@example.com',
    'created_at': date.today()
})

# Query data
users = table.select(where=lambda row: row['id'] == 1)
print(users)

# Update data
table.update(
    {'email': 'newemail@example.com'},
    where=lambda row: row['id'] == 1
)

# Delete data
table.delete(where=lambda row: row['id'] == 1)

# Save database
db.save('myapp.db.json')

# Load database
db2 = Database.load('myapp.db.json')
```

## Using SQL Parser

Execute SQL statements:

```python
from rdbms import Database, SQLParser

db = Database('myapp')
parser = SQLParser(db)

# Create table
parser.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100),
        price FLOAT
    )
""")

# Insert
parser.execute("INSERT INTO products (id, name, price) VALUES (1, 'Widget', 19.99)")

# Query
results = parser.execute("SELECT * FROM products WHERE price < 50")
print(results)

# Update
parser.execute("UPDATE products SET price = 24.99 WHERE id = 1")

# Delete
parser.execute("DELETE FROM products WHERE id = 1")
```

## Supported SQL Syntax

### CREATE TABLE
```sql
CREATE TABLE table_name (
    col1 INTEGER PRIMARY KEY,
    col2 VARCHAR(50) NOT NULL,
    col3 FLOAT,
    col4 BOOLEAN,
    col5 DATE UNIQUE
);
```

### INSERT
```sql
INSERT INTO table_name (col1, col2, col3) VALUES (1, 'value', 3.14);
```

### SELECT
```sql
-- Simple select
SELECT * FROM table_name;
SELECT col1, col2 FROM table_name;

-- With WHERE
SELECT * FROM table_name WHERE col1 = 10;
SELECT * FROM table_name WHERE col1 > 5;

-- JOIN
SELECT * FROM table1 JOIN table2 ON table1.id = table2.fk_id;
SELECT * FROM table1 LEFT JOIN table2 ON table1.id = table2.fk_id;
```

### UPDATE
```sql
UPDATE table_name SET col1 = 'new_value' WHERE col2 = 10;
UPDATE table_name SET col1 = 100, col2 = 'text' WHERE id = 1;
```

### DELETE
```sql
DELETE FROM table_name WHERE col1 = 5;
```

### CREATE INDEX
```sql
CREATE INDEX idx_name ON table_name (column_name);
CREATE UNIQUE INDEX idx_name ON table_name (column_name);
```

### DROP TABLE
```sql
DROP TABLE table_name;
```

## Data Types

| Type | Description | Example |
|------|-------------|---------|
| `INTEGER` | Whole numbers | `42`, `-10` |
| `VARCHAR(n)` | String up to n characters | `'Hello'` |
| `FLOAT` | Floating point numbers | `3.14`, `2.0` |
| `BOOLEAN` | True/False values | `TRUE`, `FALSE` |
| `DATE` | Date values | `'2026-01-16'` |

## Constraints

- **PRIMARY KEY** - Unique identifier, automatically creates unique index
- **UNIQUE** - Ensures column values are unique
- **NOT NULL** - Requires a value (no NULL allowed)

## Advanced Features

### Indexing

Indexes speed up lookups on specific columns:

```python
# Automatic indexes are created for PRIMARY KEY and UNIQUE columns
# Manual index creation:
table.create_index('column_name', unique=False)

# Or via SQL:
parser.execute("CREATE INDEX idx_name ON table (column)")
```

### JOIN Operations

Combine data from multiple tables:

```python
# Inner join (only matching rows)
result = db.join('orders', 'customers', 'customer_id', 'id', join_type='inner')

# Left join (all left table rows, with NULLs for non-matching right rows)
result = db.join('orders', 'customers', 'customer_id', 'id', join_type='left')
```

### Persistence

Save and restore database state:

```python
# Save to file
db.save('database.json')

# Load from file
db = Database.load('database.json')
```

## Tips

1. **Use the REPL for exploration** - Great for testing queries
2. **Enable indexes on frequently queried columns** - Improves performance
3. **Use constraints to maintain data integrity** - PRIMARY KEY, UNIQUE, NOT NULL
4. **Save your database regularly** - Persistence is manual, not automatic
5. **Test SQL syntax in the web console** - Visual feedback on results

## Troubleshooting

### Common Errors

**"Column X does not exist"**
- Check table structure with `DESCRIBE table_name` in REPL
- Verify column names in your query

**"Duplicate value for unique column"**
- PRIMARY KEY or UNIQUE constraint violation
- Check existing data before inserting

**"Invalid value for column"**
- Type mismatch (e.g., string for INTEGER)
- Use correct data type in VALUES clause

**"Table X already exists"**
- Drop existing table first: `DROP TABLE X`
- Or use a different table name

## Next Steps

- Explore the web application source code in `webapp/app.py`
- Read the core implementation in `rdbms/` directory
- Review tests in `tests/` for usage examples
- Modify and extend for your own projects!

## Contributing

This is an educational project demonstrating database fundamentals. Feel free to:
- Add new features (aggregate functions, subqueries, etc.)
- Improve performance (better indexing, query optimization)
- Extend SQL syntax support
- Add more data types

## License

MIT License - See LICENSE file for details.
