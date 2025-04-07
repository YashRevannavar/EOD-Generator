import os
import subprocess
import logging
from environment.constants import root_path

class GitLogFetcher:
    def __init__(self, root_path: str = root_path):
        self.root_path = root_path

    def get_git_repo_paths(self) -> list:
        """
        Returns a list of paths under root_path that are Git repositories.
        """
        logging.info("Searching for Git repositories")
        git_repos = []
        for dirpath, dir_names, filenames in os.walk(self.root_path):
            if ".git" in dir_names:
                git_repos.append(dirpath)
                dir_names.remove(".git")
        logging.info(f"Found {len(git_repos)} Git repositories")
        return git_repos

    def get_git_logs(self, days: int = 1) -> list:
        """
        Returns a list of logs for all Git repositories under root_path.
        """
        logging.info(f"Getting git logs for past {days} day(s)")
        logs = []
        for repo_path in self.get_git_repo_paths():
            logs.append(self.get_git_logs_for_single_repo(repo_path, days=days))
        return logs

    def get_git_logs_for_single_repo(self, repo_path: str, days: int = 1) -> str:
        """
        Returns logs for a single Git repository based on past number of days.
        """
        logging.info(f"Getting logs for repository: {repo_path}")
        script_path = "git_components/eod_git_connector.sh"
        command = [script_path, "--path", repo_path, "--days", str(days)]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logging.error(f"Error getting git logs: {e.stderr}")
            raise e

    def get_git_logs_by_date_range(self, start_date: str, end_date: str) -> list:
        """
        Returns logs for all Git repositories between given start and end dates.
        Dates must be in 'YYYY-MM-DD' format.
        """
        logging.info(f"Getting git logs from {start_date} to {end_date}")
        logs = []
        script_path = "git_components/sprint_review_git_connector.sh"
        for repo_path in self.get_git_repo_paths():
            command = [
                script_path,
                "--path", repo_path,
                "--start-date", start_date,
                "--end-date", end_date
            ]
            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                logs.append(result.stdout.strip())
            except subprocess.CalledProcessError as e:
                logging.error(f"Error getting git logs for {repo_path}: {e.stderr}")
                raise e
        return logs