"""
Tests for the RDBMS data types.
"""
import unittest
from datetime import date
from rdbms.data_types import Integer, VarChar, Float, Boolean, Date


class TestDataTypes(unittest.TestCase):
    
    def test_integer(self):
        int_type = Integer()
        self.assertTrue(int_type.validate(42))
        self.assertTrue(int_type.validate(-10))
        self.assertFalse(int_type.validate(3.14))
        self.assertFalse(int_type.validate("42"))
        self.assertFalse(int_type.validate(True))
        
        # Test casting
        self.assertEqual(int_type.cast(42), 42)
        self.assertEqual(int_type.cast("42"), 42)
    
    def test_varchar(self):
        varchar_type = VarChar(max_length=10)
        self.assertTrue(varchar_type.validate("hello"))
        self.assertFalse(varchar_type.validate("this is too long"))
        
        # Test casting
        self.assertEqual(varchar_type.cast("test"), "test")
        self.assertEqual(varchar_type.cast(123), "123")
        
        # Test max length
        with self.assertRaises(ValueError):
            varchar_type.cast("this is way too long")
    
    def test_float(self):
        float_type = Float()
        self.assertTrue(float_type.validate(3.14))
        self.assertTrue(float_type.validate(42))
        self.assertFalse(float_type.validate("3.14"))
        
        # Test casting
        self.assertEqual(float_type.cast(3.14), 3.14)
        self.assertEqual(float_type.cast(42), 42.0)
    
    def test_boolean(self):
        bool_type = Boolean()
        self.assertTrue(bool_type.validate(True))
        self.assertTrue(bool_type.validate(False))
        self.assertFalse(bool_type.validate(1))
        
        # Test casting
        self.assertTrue(bool_type.cast(True))
        self.assertTrue(bool_type.cast("true"))
        self.assertTrue(bool_type.cast("1"))
        self.assertFalse(bool_type.cast(False))
    
    def test_date(self):
        date_type = Date()
        today = date.today()
        self.assertTrue(date_type.validate(today))
        self.assertFalse(date_type.validate("2026-01-16"))
        
        # Test casting
        self.assertEqual(date_type.cast(today), today)
        self.assertEqual(date_type.cast("2026-01-16"), date(2026, 1, 16))
    
    def test_nullable(self):
        nullable_int = Integer(nullable=True)
        non_nullable_int = Integer(nullable=False)
        
        self.assertTrue(nullable_int.validate(None))
        self.assertFalse(non_nullable_int.validate(None))
        
        self.assertIsNone(nullable_int.cast(None))
        with self.assertRaises(ValueError):
            non_nullable_int.cast(None)


if __name__ == '__main__':
    unittest.main()
