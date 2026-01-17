"""
Index implementation for fast lookups.
"""
from typing import Any, List, Dict, Optional


class Index:
    """Simple index structure for fast lookups."""
    
    def __init__(self, column_name: str, unique: bool = False):
        self.column_name = column_name
        self.unique = unique
        # Map from value to list of row IDs
        self.index: Dict[Any, List[int]] = {}
    
    def add(self, value: Any, row_id: int):
        """Add a value to the index."""
        if value not in self.index:
            self.index[value] = []
        self.index[value].append(row_id)
    
    def remove(self, value: Any, row_id: int):
        """Remove a value from the index."""
        if value in self.index:
            if row_id in self.index[value]:
                self.index[value].remove(row_id)
            if not self.index[value]:
                del self.index[value]
    
    def lookup(self, value: Any) -> List[int]:
        """Look up row IDs by value."""
        return self.index.get(value, [])
    
    def shift_after(self, deleted_row_id: int):
        """Shift row IDs after a deletion."""
        for value, row_ids in self.index.items():
            self.index[value] = [
                row_id - 1 if row_id > deleted_row_id else row_id
                for row_id in row_ids
            ]
