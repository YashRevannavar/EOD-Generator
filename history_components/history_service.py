import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import uuid
from services.interfaces import IHistoryService # Import the interface
from models import HistoryEntry # Import HistoryEntry from models.py

# HistoryEntry class definition removed

class HistoryService(IHistoryService): # Inherit from the interface
    HISTORY_FILE = "data/.history.json"

    def __init__(self):
        self.ensure_history_file()

    def ensure_history_file(self) -> None:
        """Ensure the history file and directory exist"""
        os.makedirs(os.path.dirname(self.HISTORY_FILE), exist_ok=True)
        if not os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, 'w') as f:
                json.dump([], f)

    def load_history(self) -> List[Dict]:
        """Load history from file with error handling"""
        try:
            with open(self.HISTORY_FILE, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    print(f"Error decoding {self.HISTORY_FILE}, creating new history")
                    return []
        except FileNotFoundError:
            self.ensure_history_file()
            return []

    def save_history(self, history: List[Dict]) -> None:
        """Save history to file with error handling"""
        try:
            with open(self.HISTORY_FILE, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {str(e)}")
            raise

    def add_entry(self, entry: HistoryEntry) -> None:
        """Add a new entry to history"""
        try:
            history = self.load_history()
            history.append(entry.to_dict())
            self.save_history(history)
        except Exception as e:
            print(f"Error adding history entry: {str(e)}")
            raise

    def get_all_entries(self) -> List[HistoryEntry]:
        """Get all history entries sorted by date"""
        try:
            history = self.load_history()
            entries = [HistoryEntry.from_dict(entry) for entry in history]
            return sorted(entries, key=lambda x: x.date, reverse=True)
        except Exception as e:
            print(f"Error retrieving history entries: {str(e)}")
            raise

    def clear_history(self) -> None:
        """Clear all history entries"""
        try:
            self.save_history([])
        except Exception as e:
            print(f"Error clearing history: {str(e)}")
            raise

    def get_entry_by_id(self, entry_id: str) -> Optional[HistoryEntry]:
        """Get a specific entry by ID"""
        try:
            history = self.load_history()
            for entry in history:
                if entry["id"] == entry_id:
                    return HistoryEntry.from_dict(entry)
            return None
        except Exception as e:
            print(f"Error retrieving entry: {str(e)}")
            raise

    def delete_entry(self, entry_id: str) -> bool:
        """Delete a specific entry by ID"""
        try:
            history = self.load_history()
            filtered_history = [entry for entry in history if entry["id"] != entry_id]
            if len(filtered_history) < len(history):
                self.save_history(filtered_history)
                return True
            return False
        except Exception as e:
            print(f"Error deleting entry: {str(e)}")
            raise

    def update_entry(self, entry_id: str, updated_entry: HistoryEntry) -> bool:
        """Update a specific entry by ID"""
        try:
            history = self.load_history()
            for i, entry in enumerate(history):
                if entry["id"] == entry_id:
                    history[i] = updated_entry.to_dict()
                    self.save_history(history)
                    return True
            return False
        except Exception as e:
            print(f"Error updating entry: {str(e)}")
            raise