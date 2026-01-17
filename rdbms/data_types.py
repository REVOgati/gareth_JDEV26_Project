"""
Data type definitions for the RDBMS.
"""
from datetime import date
from typing import Any, Union


class DataType:
    """Base class for all data types."""
    
    def __init__(self, nullable=True):
        self.nullable = nullable
    
    def validate(self, value: Any) -> bool:
        """Validate if a value matches this data type."""
        if value is None:
            return self.nullable
        return self._validate_value(value)
    
    def _validate_value(self, value: Any) -> bool:
        """Override in subclasses to implement type-specific validation."""
        raise NotImplementedError
    
    def cast(self, value: Any) -> Any:
        """Cast a value to this data type."""
        if value is None:
            if not self.nullable:
                raise ValueError("NULL value not allowed for non-nullable column")
            return None
        return self._cast_value(value)
    
    def _cast_value(self, value: Any) -> Any:
        """Override in subclasses to implement type-specific casting."""
        raise NotImplementedError


class Integer(DataType):
    """Integer data type."""
    
    def _validate_value(self, value: Any) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)
    
    def _cast_value(self, value: Any) -> int:
        return int(value)
    
    def __repr__(self):
        return "INTEGER"


class VarChar(DataType):
    """Variable-length character string."""
    
    def __init__(self, max_length=255, nullable=True):
        super().__init__(nullable)
        self.max_length = max_length
    
    def _validate_value(self, value: Any) -> bool:
        return isinstance(value, str) and len(value) <= self.max_length
    
    def _cast_value(self, value: Any) -> str:
        result = str(value)
        if len(result) > self.max_length:
            raise ValueError(f"String length {len(result)} exceeds max length {self.max_length}")
        return result
    
    def __repr__(self):
        return f"VARCHAR({self.max_length})"


class Float(DataType):
    """Floating point number."""
    
    def _validate_value(self, value: Any) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    
    def _cast_value(self, value: Any) -> float:
        return float(value)
    
    def __repr__(self):
        return "FLOAT"


class Boolean(DataType):
    """Boolean data type."""
    
    def _validate_value(self, value: Any) -> bool:
        return isinstance(value, bool)
    
    def _cast_value(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        return bool(value)
    
    def __repr__(self):
        return "BOOLEAN"


class Date(DataType):
    """Date data type."""
    
    def _validate_value(self, value: Any) -> bool:
        return isinstance(value, date)
    
    def _cast_value(self, value: Any) -> date:
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            # Parse ISO format YYYY-MM-DD
            parts = value.split('-')
            if len(parts) != 3:
                raise ValueError(f"Invalid date format: {value}")
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        raise ValueError(f"Cannot cast {type(value)} to DATE")
    
    def __repr__(self):
        return "DATE"
