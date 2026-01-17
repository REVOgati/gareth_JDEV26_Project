"""
Tests for the RDBMS table operations.
"""
import unittest
from rdbms.table import Table, Column
from rdbms.data_types import Integer, VarChar


class TestTable(unittest.TestCase):
    
    def setUp(self):
        """Create a test table."""
        self.table = Table('users', [
            Column('id', Integer(nullable=False), primary_key=True),
            Column('name', VarChar(50, nullable=False)),
            Column('email', VarChar(100), unique=True)
        ])
    
    def test_insert(self):
        row_id = self.table.insert({'id': 1, 'name': 'Alice', 'email': 'alice@test.com'})
        self.assertEqual(row_id, 0)
        self.assertEqual(len(self.table.rows), 1)
        
        # Test required column
        with self.assertRaises(ValueError):
            self.table.insert({'id': 2, 'email': 'bob@test.com'})
    
    def test_unique_constraint(self):
        self.table.insert({'id': 1, 'name': 'Alice', 'email': 'alice@test.com'})
        
        # Duplicate primary key
        with self.assertRaises(ValueError):
            self.table.insert({'id': 1, 'name': 'Bob', 'email': 'bob@test.com'})
        
        # Duplicate unique column
        with self.assertRaises(ValueError):
            self.table.insert({'id': 2, 'name': 'Bob', 'email': 'alice@test.com'})
    
    def test_select(self):
        self.table.insert({'id': 1, 'name': 'Alice', 'email': 'alice@test.com'})
        self.table.insert({'id': 2, 'name': 'Bob', 'email': 'bob@test.com'})
        
        # Select all
        rows = self.table.select()
        self.assertEqual(len(rows), 2)
        
        # Select specific columns
        rows = self.table.select(columns=['id', 'name'])
        self.assertEqual(len(rows[0]), 2)
        self.assertIn('id', rows[0])
        self.assertIn('name', rows[0])
        
        # Select with WHERE
        rows = self.table.select(where=lambda row: row['id'] == 1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['name'], 'Alice')
    
    def test_update(self):
        self.table.insert({'id': 1, 'name': 'Alice', 'email': 'alice@test.com'})
        self.table.insert({'id': 2, 'name': 'Bob', 'email': 'bob@test.com'})
        
        # Update
        count = self.table.update({'name': 'Alice Smith'}, where=lambda row: row['id'] == 1)
        self.assertEqual(count, 1)
        
        rows = self.table.select(where=lambda row: row['id'] == 1)
        self.assertEqual(rows[0]['name'], 'Alice Smith')
        
        # Update with unique constraint violation
        with self.assertRaises(ValueError):
            self.table.update({'email': 'bob@test.com'}, where=lambda row: row['id'] == 1)
    
    def test_delete(self):
        self.table.insert({'id': 1, 'name': 'Alice', 'email': 'alice@test.com'})
        self.table.insert({'id': 2, 'name': 'Bob', 'email': 'bob@test.com'})
        
        count = self.table.delete(where=lambda row: row['id'] == 1)
        self.assertEqual(count, 1)
        self.assertEqual(len(self.table.rows), 1)
        
        rows = self.table.select()
        self.assertEqual(rows[0]['name'], 'Bob')
    
    def test_index(self):
        # Primary key index should be created automatically
        self.assertIn('id', self.table.indexes)
        self.assertIn('email', self.table.indexes)
        
        # Create a new index
        self.table.create_index('name')
        self.assertIn('name', self.table.indexes)


if __name__ == '__main__':
    unittest.main()
