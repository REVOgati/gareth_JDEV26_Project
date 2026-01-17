"""
Interactive REPL for the RDBMS.
"""
import sys
from .database import Database
from .sql_parser import SQLParser


class REPL:
    """Interactive REPL for executing SQL commands."""
    
    def __init__(self, database: Database):
        self.database = database
        self.parser = SQLParser(database)
    
    def run(self):
        """Run the REPL."""
        print("=" * 60)
        print("Simple RDBMS - Interactive SQL Shell")
        print("=" * 60)
        print(f"Database: {self.database.name}")
        print("Type 'help' for commands, 'exit' or 'quit' to exit")
        print("=" * 60)
        print()
        
        while True:
            try:
                # Read input
                sql = input("sql> ").strip()
                
                if not sql:
                    continue
                
                # Handle special commands
                if sql.lower() in ('exit', 'quit'):
                    print("Goodbye!")
                    break
                
                if sql.lower() == 'help':
                    self._print_help()
                    continue
                
                if sql.lower() == 'tables':
                    self._list_tables()
                    continue
                
                if sql.lower().startswith('describe '):
                    table_name = sql.split()[1]
                    self._describe_table(table_name)
                    continue
                
                # Execute SQL
                result = self.parser.execute(sql)
                
                # Display result
                if isinstance(result, list):
                    self._print_table(result)
                else:
                    print(result)
                print()
                
            except KeyboardInterrupt:
                print("\nUse 'exit' or 'quit' to exit")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                print()
    
    def _print_help(self):
        """Print help information."""
        print()
        print("SQL Commands:")
        print("  CREATE TABLE name (col1 TYPE, col2 TYPE PRIMARY KEY, ...)")
        print("  DROP TABLE name")
        print("  INSERT INTO name (col1, col2) VALUES (val1, val2)")
        print("  SELECT col1, col2 FROM name [WHERE condition]")
        print("  SELECT * FROM table1 JOIN table2 ON table1.col = table2.col")
        print("  UPDATE name SET col1=val1 WHERE condition")
        print("  DELETE FROM name WHERE condition")
        print("  CREATE INDEX idx_name ON table (column)")
        print()
        print("Data Types:")
        print("  INTEGER, FLOAT, VARCHAR(n), BOOLEAN, DATE")
        print()
        print("Constraints:")
        print("  PRIMARY KEY, UNIQUE, NOT NULL")
        print()
        print("Special Commands:")
        print("  help      - Show this help")
        print("  tables    - List all tables")
        print("  describe <table> - Show table structure")
        print("  exit/quit - Exit the REPL")
        print()
    
    def _list_tables(self):
        """List all tables."""
        tables = self.database.list_tables()
        if tables:
            print("\nTables:")
            for table in tables:
                print(f"  - {table}")
            print()
        else:
            print("\nNo tables found\n")
    
    def _describe_table(self, table_name: str):
        """Describe table structure."""
        try:
            table = self.database.get_table(table_name)
            print(f"\nTable: {table_name}")
            print("-" * 60)
            print(f"{'Column':<20} {'Type':<20} {'Constraints':<20}")
            print("-" * 60)
            
            for col_name in table.column_order:
                col = table.columns[col_name]
                constraints = []
                if col.primary_key:
                    constraints.append("PRIMARY KEY")
                if col.unique and not col.primary_key:
                    constraints.append("UNIQUE")
                if not col.data_type.nullable:
                    constraints.append("NOT NULL")
                
                constraints_str = ", ".join(constraints) if constraints else ""
                print(f"{col_name:<20} {str(col.data_type):<20} {constraints_str:<20}")
            
            print("-" * 60)
            print(f"Rows: {len(table.rows)}")
            print()
        except Exception as e:
            print(f"Error: {e}\n")
    
    def _print_table(self, rows: list):
        """Print query results as a table."""
        if not rows:
            print("(0 rows)")
            return
        
        # Get column names
        columns = list(rows[0].keys())
        
        # Calculate column widths
        widths = {}
        for col in columns:
            widths[col] = len(col)
            for row in rows:
                val = str(row[col]) if row[col] is not None else "NULL"
                widths[col] = max(widths[col], len(val))
        
        # Print header
        print()
        header = " | ".join(col.ljust(widths[col]) for col in columns)
        print(header)
        print("-" * len(header))
        
        # Print rows
        for row in rows:
            values = []
            for col in columns:
                val = str(row[col]) if row[col] is not None else "NULL"
                values.append(val.ljust(widths[col]))
            print(" | ".join(values))
        
        print(f"\n({len(rows)} row{'s' if len(rows) != 1 else ''})")


def main():
    """Main entry point for the REPL."""
    db_name = sys.argv[1] if len(sys.argv) > 1 else "default"
    db = Database(db_name)
    repl = REPL(db)
    repl.run()


if __name__ == '__main__':
    main()
