import logging

from git_components.git_service import GitLogFetcher
from llm_components.llm_connector import llm_eod_summary_generator, llm_sprint_review_summary_generator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

git_log_fetcher: GitLogFetcher = GitLogFetcher()


def run_eod():
    """Generate End of Day summary from git logs"""
    logging.info("Starting EOD Generator")
    eod_logs = git_log_fetcher.get_git_logs(days=1)
    logging.info("Git logs retrieved successfully")
    responses = llm_eod_summary_generator(collected_commits=eod_logs)
    logging.info("Summary generated successfully")
    return responses


def run_sprint_review(start_date: str, end_date: str, tickets: list[str]):
    """Generate Sprint Review summary from git logs and tickets

    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        tickets (list[str]): List of ticket details
    """
    logging.info(f"Fetching Git logs from {start_date} to {end_date}...")
    sprint_review_logs = git_log_fetcher.get_git_logs_by_date_range(start_date, end_date)
    logging.info("Git logs retrieved successfully")
    summary = llm_sprint_review_summary_generator(collected_commits=sprint_review_logs, tickets=tickets)
    logging.info("Summary generated successfully")
    return summary


if __name__ == "__main__":
    # This is now handled by streamlit_app.py
    pass
