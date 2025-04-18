import uuid
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

# --- History Model ---

class HistoryEntry(BaseModel):
    """Represents a single entry in the generation history."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str # e.g., "EOD", "SPRINT_REVIEW"
    date: str = Field(default_factory=lambda: datetime.now().isoformat())
    response: str # The generated summary or error message
    status: str # e.g., "passed", "error"

    # Keep to_dict and from_dict if they are used extensively elsewhere,
    # otherwise rely on Pydantic's built-in .dict() and parsing.
    # If keeping, ensure they align with Pydantic fields.
    def to_dict(self) -> Dict:
         # Pydantic v1 style, adjust if using v2 (model_dump)
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict) -> 'HistoryEntry':
        # Pydantic v1 style, adjust if using v2 (model_validate)
        return cls(**data)


# --- LLM Summary Models ---

# EOD Models
class CommitSummary(BaseModel):
    scope: str = Field(description="Area of focus extracted from commit message")
    description: str = Field(description="Brief description of the change")
    purpose: str = Field(default="", description="Optional purpose or rationale for the change")

class BranchSummary(BaseModel):
    name: str = Field(description="Name of the branch")
    commits: List[CommitSummary] = Field(description="List of commits in this branch")

class RepositorySummary(BaseModel):
    name: str = Field(description="Name of the repository")
    branches: List[BranchSummary] = Field(description="List of branches with commits")

class DailySummary(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    repositories: List[RepositorySummary] = Field(description="List of repositories with commits")

# Sprint Review Models
class TicketSummary(BaseModel):
    ticket_id: str = Field(description="Ticket identifier (e.g., TICKET-123)")
    branch_name: str = Field(description="Name of the Git branch")
    summary: str = Field(description="Business-focused summary of completed work")

# Wrapper model for Sprint Review output
class SprintReviewSummary(BaseModel):
    tickets: List[TicketSummary] = Field(description="List of summaries for each ticket")