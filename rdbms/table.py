"""
Table structure and data storage.
"""
from typing import List, Dict, Any, Optional
from .data_types import DataType
from .index import Index


class Column:
    """Represents a table column."""
    
    def __init__(self, name: str, data_type: DataType, primary_key=False, unique=False):
        self.name = name
        self.data_type = data_type
        self.primary_key = primary_key
        self.unique = unique
        
        if primary_key:
            self.data_type.nullable = False
            self.unique = True


class Table:
    """Represents a database table."""
    
    def __init__(self, name: str, columns: List[Column]):
        self.name = name
        self.columns = {col.name: col for col in columns}
        self.column_order = [col.name for col in columns]
        self.rows: List[Dict[str, Any]] = []
        self.indexes: Dict[str, Index] = {}
        
        # Create indexes for primary key and unique columns
        for col in columns:
            if col.primary_key or col.unique:
                self.create_index(col.name, unique=True)
        
        # Find primary key
        self.primary_key = None
        for col in columns:
            if col.primary_key:
                self.primary_key = col.name
                break
    
    def create_index(self, column_name: str, unique=False):
        """Create an index on a column."""
        if column_name not in self.columns:
            raise ValueError(f"Column {column_name} does not exist")
        
        index = Index(column_name, unique)
        # Build index from existing rows
        for row_id, row in enumerate(self.rows):
            index.add(row[column_name], row_id)
        
        self.indexes[column_name] = index
    
    def insert(self, values: Dict[str, Any]) -> int:
        """Insert a row into the table."""
        # Validate all required columns are present
        for col_name in self.column_order:
            if col_name not in values:
                if not self.columns[col_name].data_type.nullable:
                    raise ValueError(f"Column {col_name} is required")
                values[col_name] = None
        
        # Cast and validate values
        row = {}
        for col_name, value in values.items():
            if col_name not in self.columns:
                raise ValueError(f"Column {col_name} does not exist")
            
            col = self.columns[col_name]
            # Cast first, then validate the casted value
            try:
                casted_value = col.data_type.cast(value)
                row[col_name] = casted_value
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid value for column {col_name}: {value} - {str(e)}")
        
        # Check unique constraints via indexes
        for col_name, index in self.indexes.items():
            if index.unique and row[col_name] is not None:
                if index.lookup(row[col_name]):
                    raise ValueError(f"Duplicate value for unique column {col_name}: {row[col_name]}")
        
        # Insert row
        row_id = len(self.rows)
        self.rows.append(row)
        
        # Update indexes
        for col_name, index in self.indexes.items():
            index.add(row[col_name], row_id)
        
        return row_id
    
    def select(self, columns: Optional[List[str]] = None, where: Optional[callable] = None) -> List[Dict[str, Any]]:
        """Select rows from the table."""
        if columns is None:
            columns = self.column_order
        
        # Validate columns
        for col in columns:
            if col not in self.columns:
                raise ValueError(f"Column {col} does not exist")
        
        # Filter rows
        result = []
        for row in self.rows:
            if where is None or where(row):
                result.append({col: row[col] for col in columns})
        
        return result
    
    def update(self, values: Dict[str, Any], where: Optional[callable] = None) -> int:
        """Update rows in the table."""
        # Validate and cast new values
        updates = {}
        for col_name, value in values.items():
            if col_name not in self.columns:
                raise ValueError(f"Column {col_name} does not exist")
            
            col = self.columns[col_name]
            if not col.data_type.validate(value):
                raise ValueError(f"Invalid value for column {col_name}: {value}")
            
            updates[col_name] = col.data_type.cast(value)
        
        # Update matching rows
        count = 0
        for row_id, row in enumerate(self.rows):
            if where is None or where(row):
                # Check unique constraints for updated values
                for col_name in updates:
                    if col_name in self.indexes and self.indexes[col_name].unique:
                        # Remove old value from index temporarily
                        old_val = row[col_name]
                        self.indexes[col_name].remove(old_val, row_id)
                        
                        # Check if new value violates uniqueness
                        if updates[col_name] is not None:
                            existing = self.indexes[col_name].lookup(updates[col_name])
                            if existing:
                                # Restore old value and raise error
                                self.indexes[col_name].add(old_val, row_id)
                                raise ValueError(f"Duplicate value for unique column {col_name}: {updates[col_name]}")
                        
                        # Re-add with new value
                        self.indexes[col_name].add(updates[col_name], row_id)
                
                # Apply updates
                row.update(updates)
                count += 1
        
        return count
    
    def delete(self, where: Optional[callable] = None) -> int:
        """Delete rows from the table."""
        to_delete = []
        for row_id, row in enumerate(self.rows):
            if where is None or where(row):
                to_delete.append(row_id)
        
        # Delete in reverse order to maintain indices
        for row_id in reversed(to_delete):
            row = self.rows[row_id]
            
            # Remove from indexes
            for col_name, index in self.indexes.items():
                index.remove(row[col_name], row_id)
            
            # Remove row
            del self.rows[row_id]
            
            # Update indexes for shifted rows
            for col_name, index in self.indexes.items():
                index.shift_after(row_id)
        
        return len(to_delete)
