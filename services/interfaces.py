from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
# Import models from the central models.py file
from models import DailySummary, SprintReviewSummary, HistoryEntry

class IGitService(ABC):
    @abstractmethod
    def get_git_logs(self, days: int = 1) -> str: # Assuming combined logs as string
        pass

    @abstractmethod
    def get_git_logs_by_date_range(self, start_date: str, end_date: str) -> str: # Assuming combined logs as string
        pass

class ILlmService(ABC):
    @abstractmethod
    def generate_eod_summary(self, collected_commits: str) -> DailySummary:
        pass

    @abstractmethod
    def generate_sprint_review(self, collected_commits: str, tickets: str) -> SprintReviewSummary:
        pass

class IHistoryService(ABC):
    @abstractmethod
    def add_entry(self, entry: HistoryEntry) -> None:
        pass

    @abstractmethod
    def get_all_entries(self) -> List[HistoryEntry]:
        pass

    @abstractmethod
    def get_entry_by_id(self, entry_id: str) -> Optional[HistoryEntry]:
        pass

    @abstractmethod
    def delete_entry(self, entry_id: str) -> bool:
        pass

    @abstractmethod
    def clear_history(self) -> None:
        pass

    # Add other methods like update_entry if needed by the service layer