import logging

from git_components.git_service import GitLogFetcher
from llm_components.llm_connector import llm_summary_generator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

git_log_fetcher: GitLogFetcher = GitLogFetcher()


def run_eod():
    logging.info("Starting EOD Generator")
    logging.info("Git logs retrieved successfully")
    eod_logs = git_log_fetcher.get_git_logs(days=1)
    responses = llm_summary_generator(collected_commits=eod_logs)
    logging.info("Summary generated successfully")
    logging.info(f"\n\n{responses}")
    return None


def run_sprint_review():
    start_date = input("Enter the start date (DD.MM.YY): ")
    end_date = input("Enter the end date (DD.MM.YY): ")
    print("Enter ticket details (type 'done' when finished):")
    tickets = []
    while True:
        ticket = input("- ")
        if ticket.lower() == "done":
            break
        tickets.append(ticket)
    logging.info(f"Collected tickets: {tickets}")
    logging.info(f"Fetching Git logs from {start_date} to {end_date}...")
    # Placeholder for fetching Git logs based on dates
    sprint_review_logs = git_log_fetcher.get_git_logs_by_date_range(start_date, end_date)
    logging.info("Git logs retrieved successfully")
    # Placeholder for generating prompt and summary
    # prompt = f"Tickets: {tickets}\nGit Logs: {git_logs}"
    # summary = llm_summary_generator(collected_commits=git_logs)
    # print("\nGenerated Summary:")
    # print(summary)
    return None

def test_llm():
    pass


if __name__ == "__main__":
    while True:
        print("\nChoose an option:")
        print("1. EOD - Run the current code.")
        print("2. Sprint Review - Collect and process sprint details.")
        print("3. Quit - Exit the program.")
        choice = input("Enter your choice (1/2/3): ")

        if choice == "1":
            run_eod()
            break
        elif choice == "2":
            run_sprint_review()
        elif choice == "3":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")
