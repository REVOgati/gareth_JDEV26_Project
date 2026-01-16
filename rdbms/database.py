"""
Database management and storage.
"""
from typing import Dict, Optional, List, Any
from .table import Table, Column
import json
import os


class Database:
    """Main database class."""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.tables: Dict[str, Table] = {}
    
    def create_table(self, name: str, columns: List[Column]) -> Table:
        """Create a new table."""
        if name in self.tables:
            raise ValueError(f"Table {name} already exists")
        
        table = Table(name, columns)
        self.tables[name] = table
        return table
    
    def drop_table(self, name: str):
        """Drop a table."""
        if name not in self.tables:
            raise ValueError(f"Table {name} does not exist")
        del self.tables[name]
    
    def get_table(self, name: str) -> Table:
        """Get a table by name."""
        if name not in self.tables:
            raise ValueError(f"Table {name} does not exist")
        return self.tables[name]
    
    def list_tables(self) -> List[str]:
        """List all table names."""
        return list(self.tables.keys())
    
    def join(self, left_table_name: str, right_table_name: str,
             left_column: str, right_column: str,
             join_type: str = "inner",
             select_columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Perform a join operation between two tables.
        
        Args:
            left_table_name: Name of the left table
            right_table_name: Name of the right table
            left_column: Column name in left table to join on
            right_column: Column name in right table to join on
            join_type: Type of join ("inner" or "left")
            select_columns: Optional list of columns to select (with table prefix, e.g., "users.id")
        
        Returns:
            List of joined rows
        """
        left_table = self.get_table(left_table_name)
        right_table = self.get_table(right_table_name)
        
        if left_column not in left_table.columns:
            raise ValueError(f"Column {left_column} not in table {left_table_name}")
        if right_column not in right_table.columns:
            raise ValueError(f"Column {right_column} not in table {right_table_name}")
        
        # Build index on right table for faster lookup
        right_index = {}
        for row in right_table.rows:
            key = row[right_column]
            if key not in right_index:
                right_index[key] = []
            right_index[key].append(row)
        
        result = []
        
        for left_row in left_table.rows:
            key = left_row[left_column]
            matches = right_index.get(key, [])
            
            if matches:
                # Found matching rows
                for right_row in matches:
                    joined_row = {}
                    # Add left table columns
                    for col_name, value in left_row.items():
                        joined_row[f"{left_table_name}.{col_name}"] = value
                    # Add right table columns
                    for col_name, value in right_row.items():
                        joined_row[f"{right_table_name}.{col_name}"] = value
                    result.append(joined_row)
            elif join_type.lower() == "left":
                # Left join: include left row with NULL for right columns
                joined_row = {}
                for col_name, value in left_row.items():
                    joined_row[f"{left_table_name}.{col_name}"] = value
                for col_name in right_table.columns:
                    joined_row[f"{right_table_name}.{col_name}"] = None
                result.append(joined_row)
        
        # Filter columns if specified
        if select_columns:
            result = [
                {col: row.get(col) for col in select_columns}
                for row in result
            ]
        
        return result
    
    def save(self, filepath: str):
        """Save database to a JSON file."""
        data = {
            "name": self.name,
            "tables": {}
        }
        
        for table_name, table in self.tables.items():
            table_data = {
                "columns": [
                    {
                        "name": col.name,
                        "type": str(col.data_type),
                        "nullable": col.data_type.nullable,
                        "primary_key": col.primary_key,
                        "unique": col.unique
                    }
                    for col in [table.columns[name] for name in table.column_order]
                ],
                "rows": []
            }
            
            # Serialize rows
            for row in table.rows:
                serialized_row = {}
                for col_name, value in row.items():
                    if value is None:
                        serialized_row[col_name] = None
                    elif hasattr(value, 'isoformat'):  # Date
                        serialized_row[col_name] = value.isoformat()
                    else:
                        serialized_row[col_name] = value
                table_data["rows"].append(serialized_row)
            
            data["tables"][table_name] = table_data
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'Database':
        """Load database from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        db = cls(data["name"])
        
        from .data_types import Integer, VarChar, Float, Boolean, Date
        
        for table_name, table_data in data["tables"].items():
            # Reconstruct columns
            columns = []
            for col_data in table_data["columns"]:
                # Parse type
                type_str = col_data["type"]
                if type_str.startswith("VARCHAR"):
                    max_len = int(type_str.split("(")[1].split(")")[0])
                    data_type = VarChar(max_len, nullable=col_data["nullable"])
                elif type_str == "INTEGER":
                    data_type = Integer(nullable=col_data["nullable"])
                elif type_str == "FLOAT":
                    data_type = Float(nullable=col_data["nullable"])
                elif type_str == "BOOLEAN":
                    data_type = Boolean(nullable=col_data["nullable"])
                elif type_str == "DATE":
                    data_type = Date(nullable=col_data["nullable"])
                else:
                    raise ValueError(f"Unknown type: {type_str}")
                
                column = Column(
                    col_data["name"],
                    data_type,
                    primary_key=col_data.get("primary_key", False),
                    unique=col_data.get("unique", False)
                )
                columns.append(column)
            
            table = db.create_table(table_name, columns)
            
            # Insert rows
            for row_data in table_data["rows"]:
                # Convert date strings back to date objects
                for col_name, value in row_data.items():
                    col = table.columns[col_name]
                    if isinstance(col.data_type, Date) and value is not None:
                        row_data[col_name] = col.data_type.cast(value)
                
                table.insert(row_data)
        
        return db
