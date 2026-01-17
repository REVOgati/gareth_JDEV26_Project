"""
Tests for the RDBMS SQL parser.
"""
import unittest
from datetime import date
from rdbms.database import Database
from rdbms.sql_parser import SQLParser


class TestSQLParser(unittest.TestCase):
    
    def setUp(self):
        """Create a test database and parser."""
        self.db = Database('test')
        self.parser = SQLParser(self.db)
    
    def test_create_table(self):
        sql = "CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(50) NOT NULL, email VARCHAR(100) UNIQUE)"
        result = self.parser.execute(sql)
        self.assertIn('created successfully', result)
        self.assertIn('users', self.db.tables)
        
        table = self.db.get_table('users')
        self.assertEqual(len(table.columns), 3)
        self.assertTrue(table.columns['id'].primary_key)
        self.assertTrue(table.columns['email'].unique)
    
    def test_insert(self):
        self.parser.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(50))")
        result = self.parser.execute("INSERT INTO users (id, name) VALUES (1, 'Alice')")
        self.assertIn('1 row inserted', result)
        
        table = self.db.get_table('users')
        self.assertEqual(len(table.rows), 1)
    
    def test_select(self):
        self.parser.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(50))")
        self.parser.execute("INSERT INTO users (id, name) VALUES (1, 'Alice')")
        self.parser.execute("INSERT INTO users (id, name) VALUES (2, 'Bob')")
        
        # Select all
        rows = self.parser.execute("SELECT * FROM users")
        self.assertEqual(len(rows), 2)
        
        # Select specific columns
        rows = self.parser.execute("SELECT name FROM users")
        self.assertEqual(len(rows[0]), 1)
        
        # Select with WHERE
        rows = self.parser.execute("SELECT * FROM users WHERE id = 1")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['name'], 'Alice')
    
    def test_update(self):
        self.parser.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(50))")
        self.parser.execute("INSERT INTO users (id, name) VALUES (1, 'Alice')")
        
        result = self.parser.execute("UPDATE users SET name = 'Alice Smith' WHERE id = 1")
        self.assertIn('1 row(s) updated', result)
        
        rows = self.parser.execute("SELECT * FROM users WHERE id = 1")
        self.assertEqual(rows[0]['name'], 'Alice Smith')
    
    def test_delete(self):
        self.parser.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(50))")
        self.parser.execute("INSERT INTO users (id, name) VALUES (1, 'Alice')")
        self.parser.execute("INSERT INTO users (id, name) VALUES (2, 'Bob')")
        
        result = self.parser.execute("DELETE FROM users WHERE id = 1")
        self.assertIn('1 row(s) deleted', result)
        
        rows = self.parser.execute("SELECT * FROM users")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['name'], 'Bob')
    
    def test_join(self):
        # Create tables
        self.parser.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(50))")
        self.parser.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, user_id INTEGER, title VARCHAR(100))")
        
        # Insert data
        self.parser.execute("INSERT INTO users (id, name) VALUES (1, 'Alice')")
        self.parser.execute("INSERT INTO users (id, name) VALUES (2, 'Bob')")
        self.parser.execute("INSERT INTO posts (id, user_id, title) VALUES (1, 1, 'First Post')")
        self.parser.execute("INSERT INTO posts (id, user_id, title) VALUES (2, 1, 'Second Post')")
        
        # Inner join
        rows = self.parser.execute("SELECT * FROM posts JOIN users ON posts.user_id = users.id")
        self.assertEqual(len(rows), 2)
        self.assertIn('posts.title', rows[0])
        self.assertIn('users.name', rows[0])
        
        # Left join
        self.parser.execute("INSERT INTO posts (id, user_id, title) VALUES (3, 99, 'Orphaned Post')")
        rows = self.parser.execute("SELECT * FROM posts LEFT JOIN users ON posts.user_id = users.id")
        self.assertEqual(len(rows), 3)
    
    def test_drop_table(self):
        self.parser.execute("CREATE TABLE temp (id INTEGER PRIMARY KEY)")
        result = self.parser.execute("DROP TABLE temp")
        self.assertIn('dropped successfully', result)
        self.assertNotIn('temp', self.db.tables)


if __name__ == '__main__':
    unittest.main()
