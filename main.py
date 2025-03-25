import logging
from git_components.git_service import get_git_logs
from llm_components.llm_connector import llm_summary_generator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    logging.info("Starting EOD Generator")
    logs = get_git_logs(days=1)
    logging.info("Git logs retrieved successfully")
    responses = llm_summary_generator(collected_commits=logs)
    logging.info("Summary generated successfully")
    logging.info(f"\n\n{responses}")
