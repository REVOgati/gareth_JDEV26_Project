"""
SQL parser for the RDBMS.
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from .database import Database
from .table import Column
from .data_types import Integer, VarChar, Float, Boolean, Date


class SQLParser:
    """Simple SQL parser and executor."""
    
    def __init__(self, database: Database):
        self.database = database
    
    def execute(self, sql: str) -> Any:
        """Execute a SQL statement."""
        sql = sql.strip()
        
        # Remove trailing semicolon
        if sql.endswith(';'):
            sql = sql[:-1].strip()
        
        # Determine statement type
        sql_upper = sql.upper()
        
        if sql_upper.startswith('CREATE TABLE'):
            return self._execute_create_table(sql)
        elif sql_upper.startswith('DROP TABLE'):
            return self._execute_drop_table(sql)
        elif sql_upper.startswith('INSERT INTO'):
            return self._execute_insert(sql)
        elif sql_upper.startswith('SELECT'):
            return self._execute_select(sql)
        elif sql_upper.startswith('UPDATE'):
            return self._execute_update(sql)
        elif sql_upper.startswith('DELETE FROM'):
            return self._execute_delete(sql)
        elif sql_upper.startswith('CREATE INDEX'):
            return self._execute_create_index(sql)
        else:
            raise ValueError(f"Unsupported SQL statement: {sql}")
    
    def _execute_create_table(self, sql: str) -> str:
        """Execute CREATE TABLE statement."""
        # Pattern: CREATE TABLE table_name (col1 TYPE, col2 TYPE PRIMARY KEY, ...)
        match = re.match(r'CREATE TABLE\s+(\w+)\s*\((.*)\)', sql, re.IGNORECASE | re.DOTALL)
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        
        table_name = match.group(1)
        columns_str = match.group(2)
        
        columns = []
        for col_def in columns_str.split(','):
            col_def = col_def.strip()
            parts = col_def.split()
            
            if len(parts) < 2:
                raise ValueError(f"Invalid column definition: {col_def}")
            
            col_name = parts[0]
            col_type_str = parts[1].upper()
            
            # Parse data type
            if col_type_str.startswith('VARCHAR'):
                match = re.match(r'VARCHAR\((\d+)\)', col_type_str)
                if match:
                    max_len = int(match.group(1))
                    data_type = VarChar(max_len)
                else:
                    data_type = VarChar()
            elif col_type_str == 'INTEGER' or col_type_str == 'INT':
                data_type = Integer()
            elif col_type_str == 'FLOAT':
                data_type = Float()
            elif col_type_str == 'BOOLEAN' or col_type_str == 'BOOL':
                data_type = Boolean()
            elif col_type_str == 'DATE':
                data_type = Date()
            else:
                raise ValueError(f"Unsupported data type: {col_type_str}")
            
            # Check for constraints
            primary_key = 'PRIMARY KEY' in col_def.upper()
            unique = 'UNIQUE' in col_def.upper()
            not_null = 'NOT NULL' in col_def.upper()
            
            if not_null or primary_key:
                data_type.nullable = False
            
            column = Column(col_name, data_type, primary_key=primary_key, unique=unique)
            columns.append(column)
        
        self.database.create_table(table_name, columns)
        return f"Table {table_name} created successfully"
    
    def _execute_drop_table(self, sql: str) -> str:
        """Execute DROP TABLE statement."""
        match = re.match(r'DROP TABLE\s+(\w+)', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DROP TABLE syntax")
        
        table_name = match.group(1)
        self.database.drop_table(table_name)
        return f"Table {table_name} dropped successfully"
    
    def _execute_insert(self, sql: str) -> str:
        """Execute INSERT INTO statement."""
        # Pattern: INSERT INTO table (col1, col2) VALUES (val1, val2)
        match = re.match(
            r'INSERT INTO\s+(\w+)\s*\((.*?)\)\s*VALUES\s*\((.*?)\)',
            sql,
            re.IGNORECASE | re.DOTALL
        )
        if not match:
            raise ValueError("Invalid INSERT syntax")
        
        table_name = match.group(1)
        columns_str = match.group(2)
        values_str = match.group(3)
        
        table = self.database.get_table(table_name)
        
        columns = [col.strip() for col in columns_str.split(',')]
        value_strs = self._parse_values(values_str)
        
        if len(columns) != len(value_strs):
            raise ValueError("Number of columns and values do not match")
        
        values = {}
        for col_name, val_str in zip(columns, value_strs):
            values[col_name] = self._parse_value(val_str, table.columns[col_name].data_type)
        
        row_id = table.insert(values)
        return f"1 row inserted (ID: {row_id})"
    
    def _execute_select(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SELECT statement."""
        # Handle JOIN queries
        if 'JOIN' in sql.upper():
            return self._execute_select_join(sql)
        
        # Pattern: SELECT columns FROM table [WHERE condition]
        match = re.match(
            r'SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*))?',
            sql,
            re.IGNORECASE | re.DOTALL
        )
        if not match:
            raise ValueError("Invalid SELECT syntax")
        
        columns_str = match.group(1).strip()
        table_name = match.group(2)
        where_str = match.group(3)
        
        table = self.database.get_table(table_name)
        
        # Parse columns
        if columns_str == '*':
            columns = None
        else:
            columns = [col.strip() for col in columns_str.split(',')]
        
        # Parse WHERE clause
        where_func = None
        if where_str:
            where_func = self._parse_where(where_str, table)
        
        return table.select(columns=columns, where=where_func)
    
    def _execute_select_join(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SELECT with JOIN."""
        # Pattern: SELECT columns FROM table1 [LEFT] JOIN table2 ON table1.col = table2.col
        match = re.match(
            r'SELECT\s+(.*?)\s+FROM\s+(\w+)\s+(LEFT\s+)?JOIN\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',
            sql,
            re.IGNORECASE
        )
        if not match:
            raise ValueError("Invalid SELECT JOIN syntax")
        
        columns_str = match.group(1).strip()
        left_table = match.group(2)
        is_left_join = match.group(3) is not None
        right_table = match.group(4)
        join_left_table = match.group(5)
        join_left_col = match.group(6)
        join_right_table = match.group(7)
        join_right_col = match.group(8)
        
        # Verify join table names match
        if join_left_table != left_table or join_right_table != right_table:
            raise ValueError("Join table names must match FROM and JOIN tables")
        
        # Parse columns
        if columns_str == '*':
            select_columns = None
        else:
            select_columns = [col.strip() for col in columns_str.split(',')]
        
        join_type = "left" if is_left_join else "inner"
        
        return self.database.join(
            left_table, right_table,
            join_left_col, join_right_col,
            join_type=join_type,
            select_columns=select_columns
        )
    
    def _execute_update(self, sql: str) -> str:
        """Execute UPDATE statement."""
        # Pattern: UPDATE table SET col1=val1, col2=val2 [WHERE condition]
        match = re.match(
            r'UPDATE\s+(\w+)\s+SET\s+(.*?)(?:\s+WHERE\s+(.*))?$',
            sql,
            re.IGNORECASE | re.DOTALL
        )
        if not match:
            raise ValueError("Invalid UPDATE syntax")
        
        table_name = match.group(1)
        set_str = match.group(2)
        where_str = match.group(3)
        
        table = self.database.get_table(table_name)
        
        # Parse SET clause
        updates = {}
        for assignment in set_str.split(','):
            assignment = assignment.strip()
            match = re.match(r'(\w+)\s*=\s*(.+)', assignment)
            if not match:
                raise ValueError(f"Invalid assignment: {assignment}")
            
            col_name = match.group(1)
            val_str = match.group(2).strip()
            updates[col_name] = self._parse_value(val_str, table.columns[col_name].data_type)
        
        # Parse WHERE clause
        where_func = None
        if where_str:
            where_func = self._parse_where(where_str, table)
        
        count = table.update(updates, where=where_func)
        return f"{count} row(s) updated"
    
    def _execute_delete(self, sql: str) -> str:
        """Execute DELETE FROM statement."""
        # Pattern: DELETE FROM table [WHERE condition]
        match = re.match(
            r'DELETE FROM\s+(\w+)(?:\s+WHERE\s+(.*))?',
            sql,
            re.IGNORECASE
        )
        if not match:
            raise ValueError("Invalid DELETE syntax")
        
        table_name = match.group(1)
        where_str = match.group(2)
        
        table = self.database.get_table(table_name)
        
        # Parse WHERE clause
        where_func = None
        if where_str:
            where_func = self._parse_where(where_str, table)
        
        count = table.delete(where=where_func)
        return f"{count} row(s) deleted"
    
    def _execute_create_index(self, sql: str) -> str:
        """Execute CREATE INDEX statement."""
        # Pattern: CREATE INDEX index_name ON table (column)
        match = re.match(
            r'CREATE\s+(UNIQUE\s+)?INDEX\s+\w+\s+ON\s+(\w+)\s*\((\w+)\)',
            sql,
            re.IGNORECASE
        )
        if not match:
            raise ValueError("Invalid CREATE INDEX syntax")
        
        is_unique = match.group(1) is not None
        table_name = match.group(2)
        column_name = match.group(3)
        
        table = self.database.get_table(table_name)
        table.create_index(column_name, unique=is_unique)
        
        return f"Index created on {table_name}.{column_name}"
    
    def _parse_values(self, values_str: str) -> List[str]:
        """Parse comma-separated values, handling quoted strings."""
        values = []
        current = []
        in_quotes = False
        quote_char = None
        
        for char in values_str:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
                current.append(char)
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current.append(char)
            elif char == ',' and not in_quotes:
                values.append(''.join(current).strip())
                current = []
            else:
                current.append(char)
        
        if current:
            values.append(''.join(current).strip())
        
        return values
    
    def _parse_value(self, val_str: str, data_type):
        """Parse a single value string."""
        val_str = val_str.strip()
        
        # NULL
        if val_str.upper() == 'NULL':
            return None
        
        # String (quoted)
        if (val_str.startswith('"') and val_str.endswith('"')) or \
           (val_str.startswith("'") and val_str.endswith("'")):
            return val_str[1:-1]
        
        # Boolean
        if val_str.upper() in ('TRUE', 'FALSE'):
            return val_str.upper() == 'TRUE'
        
        # Try to parse as number or use as-is
        try:
            if '.' in val_str:
                return float(val_str)
            else:
                return int(val_str)
        except ValueError:
            return val_str
    
    def _parse_where(self, where_str: str, table):
        """Parse WHERE clause and return a filter function."""
        where_str = where_str.strip()
        
        # Simple condition: column operator value
        match = re.match(r'(\w+)\s*(=|!=|<>|<|>|<=|>=)\s*(.+)', where_str)
        if not match:
            raise ValueError(f"Unsupported WHERE clause: {where_str}")
        
        col_name = match.group(1)
        operator = match.group(2)
        val_str = match.group(3).strip()
        
        if col_name not in table.columns:
            raise ValueError(f"Column {col_name} does not exist")
        
        value = self._parse_value(val_str, table.columns[col_name].data_type)
        
        def where_func(row):
            row_val = row[col_name]
            if operator == '=':
                return row_val == value
            elif operator in ('!=', '<>'):
                return row_val != value
            elif operator == '<':
                return row_val < value
            elif operator == '>':
                return row_val > value
            elif operator == '<=':
                return row_val <= value
            elif operator == '>=':
                return row_val >= value
            return False
        
        return where_func
