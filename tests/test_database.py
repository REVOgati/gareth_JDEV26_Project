"""
Tests for database operations including JOIN and persistence.
"""
import unittest
import os
import tempfile
from datetime import date
from rdbms.database import Database
from rdbms.table import Column
from rdbms.data_types import Integer, VarChar, Date


class TestDatabase(unittest.TestCase):
    
    def test_create_table(self):
        db = Database('test')
        table = db.create_table('users', [
            Column('id', Integer(nullable=False), primary_key=True),
            Column('name', VarChar(50))
        ])
        
        self.assertIn('users', db.tables)
        self.assertEqual(table.name, 'users')
    
    def test_join_inner(self):
        db = Database('test')
        
        # Create tables
        users = db.create_table('users', [
            Column('id', Integer(nullable=False), primary_key=True),
            Column('name', VarChar(50))
        ])
        
        posts = db.create_table('posts', [
            Column('id', Integer(nullable=False), primary_key=True),
            Column('user_id', Integer()),
            Column('title', VarChar(100))
        ])
        
        # Insert data
        users.insert({'id': 1, 'name': 'Alice'})
        users.insert({'id': 2, 'name': 'Bob'})
        posts.insert({'id': 1, 'user_id': 1, 'title': 'Post 1'})
        posts.insert({'id': 2, 'user_id': 1, 'title': 'Post 2'})
        
        # Inner join
        result = db.join('posts', 'users', 'user_id', 'id', join_type='inner')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['users.name'], 'Alice')
        self.assertEqual(result[0]['posts.title'], 'Post 1')
    
    def test_join_left(self):
        db = Database('test')
        
        # Create tables
        users = db.create_table('users', [
            Column('id', Integer(nullable=False), primary_key=True),
            Column('name', VarChar(50))
        ])
        
        posts = db.create_table('posts', [
            Column('id', Integer(nullable=False), primary_key=True),
            Column('user_id', Integer()),
            Column('title', VarChar(100))
        ])
        
        # Insert data
        users.insert({'id': 1, 'name': 'Alice'})
        posts.insert({'id': 1, 'user_id': 1, 'title': 'Post 1'})
        posts.insert({'id': 2, 'user_id': 99, 'title': 'Orphaned Post'})
        
        # Left join
        result = db.join('posts', 'users', 'user_id', 'id', join_type='left')
        self.assertEqual(len(result), 2)
        
        # First row should have user data
        self.assertEqual(result[0]['users.name'], 'Alice')
        
        # Second row should have NULL for user columns
        orphaned = [r for r in result if r['posts.id'] == 2][0]
        self.assertIsNone(orphaned['users.name'])
    
    def test_save_and_load(self):
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            # Create and populate database
            db = Database('test')
            table = db.create_table('users', [
                Column('id', Integer(nullable=False), primary_key=True),
                Column('name', VarChar(50)),
                Column('created_at', Date())
            ])
            table.insert({'id': 1, 'name': 'Alice', 'created_at': date(2026, 1, 1)})
            table.insert({'id': 2, 'name': 'Bob', 'created_at': date(2026, 1, 2)})
            
            # Save
            db.save(temp_file)
            
            # Load
            db2 = Database.load(temp_file)
            self.assertEqual(db2.name, 'test')
            self.assertIn('users', db2.tables)
            
            table2 = db2.get_table('users')
            self.assertEqual(len(table2.rows), 2)
            self.assertEqual(table2.rows[0]['name'], 'Alice')
            self.assertEqual(table2.rows[0]['created_at'], date(2026, 1, 1))
        
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == '__main__':
    unittest.main()
