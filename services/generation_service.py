import logging
import traceback
from typing import Tuple, Optional, Any
from .interfaces import IGitService, ILlmService, IHistoryService
# Import models from central models.py
from models import HistoryEntry, DailySummary, SprintReviewSummary

# Helper function to format DailySummary object to string (copied from main.py for now)
# TODO: Consider moving formatting logic elsewhere (e.g., dedicated formatter module or within models)
def format_daily_summary(summary: DailySummary) -> str:
    lines = []
    lines.append(f"- Date: {summary.date}")
    lines.append("") # Add a blank line after the date
    for repo in summary.repositories:
        lines.append(f"  - Repository Name: {repo.name}")
        for branch in repo.branches:
            lines.append(f"    - Branch: {branch.name}")
            for commit in branch.commits:
                purpose_str = f" {commit.purpose}" if commit.purpose else ""
                lines.append(f"      - ({commit.scope}) {commit.description}{purpose_str}")
        lines.append("") # Add a blank line between repositories
    # Remove the last blank line if it exists
    if lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)

# Helper function to format SprintReviewSummary object to string (copied from main.py for now)
# TODO: Consider moving formatting logic elsewhere
def format_sprint_review(summary_obj: SprintReviewSummary) -> str:
    lines = []
    if not summary_obj or not summary_obj.tickets:
        return "No sprint review summary generated."

    for ticket in summary_obj.tickets:
        lines.append(f"- Ticket ID: {ticket.ticket_id}")
        lines.append(f"- Branch Name: {ticket.branch_name}")
        lines.append(f"- Summary: {ticket.summary}")
        lines.append("------------") # Separator
    # Remove the last separator if it exists
    if lines and lines[-1] == "------------":
        lines.pop()
    return "\n".join(lines)

def format_error(error):
    return {
        'error': str(error),
        'traceback': traceback.format_exc()
    }

class GenerationService:
    def __init__(self, git_service: IGitService, llm_service: ILlmService, history_service: IHistoryService):
        self._git_service = git_service
        self._llm_service = llm_service
        self._history_service = history_service
        logging.info("GenerationService initialized.")

    def generate_eod_report(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Generates the EOD report.
        Returns a tuple: (formatted_summary, error_message)
        """
        try:
            logging.info("GenerationService: Starting EOD report generation.")
            eod_logs = self._git_service.get_git_logs(days=2)
            logging.info("GenerationService: Git logs retrieved.")

            summary_object = self._llm_service.generate_eod_summary(collected_commits=eod_logs)
            logging.info("GenerationService: LLM summary generated.")

            formatted_response = format_daily_summary(summary_object)
            logging.info("GenerationService: Summary formatted.")

            entry = HistoryEntry(
                type="EOD", # Corrected argument name
                response=formatted_response,
                status="passed"
            )
            self._history_service.add_entry(entry)
            logging.info("GenerationService: History entry added.")

            return formatted_response, None

        except Exception as e:
            error_details = format_error(e)
            logging.error(f"GenerationService: Error during EOD report generation: {error_details}")
            error_message = str(e)
            try:
                entry = HistoryEntry(
                    type="EOD", # Corrected argument name
                    response=error_message,
                    status="error"
                )
                self._history_service.add_entry(entry)
                logging.info("GenerationService: Error history entry added.")
            except Exception as hist_e:
                 logging.error(f"GenerationService: Failed to add error history entry: {format_error(hist_e)}")

            return None, error_message

    def generate_sprint_review_report(self, start_date: str, end_date: str, tickets: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generates the Sprint Review report.
        Returns a tuple: (formatted_summary, error_message)
        """
        try:
            logging.info(f"GenerationService: Starting Sprint Review report generation for {start_date} to {end_date}.")
            sprint_review_logs = self._git_service.get_git_logs_by_date_range(start_date, end_date)
            logging.info("GenerationService: Git logs retrieved.")

            summary_object = self._llm_service.generate_sprint_review(
                collected_commits=sprint_review_logs,
                tickets=tickets
            )
            logging.info("GenerationService: LLM summary generated.")

            formatted_summary = format_sprint_review(summary_object)
            logging.info("GenerationService: Summary formatted.")

            entry = HistoryEntry(
                type="SPRINT_REVIEW", # Corrected argument name
                response=formatted_summary,
                status="passed"
            )
            self._history_service.add_entry(entry)
            logging.info("GenerationService: History entry added.")

            return formatted_summary, None

        except Exception as e:
            error_details = format_error(e)
            logging.error(f"GenerationService: Error during Sprint Review report generation: {error_details}")
            error_message = str(e)
            try:
                entry = HistoryEntry(
                    type="SPRINT_REVIEW", # Corrected argument name
                    response=error_message,
                    status="error"
                )
                self._history_service.add_entry(entry)
                logging.info("GenerationService: Error history entry added.")
            except Exception as hist_e:
                 logging.error(f"GenerationService: Failed to add error history entry: {format_error(hist_e)}")

            return None, error_message