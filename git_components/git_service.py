import os
import subprocess
import logging
from environment.constants import root_path

def get_git_repo_paths(root_path: str) -> list:
    """
    Returns a list of paths under root_path that are Git repositories.
    """
    logging.info("Searching for Git repositories")
    git_repos = []
    for dirpath, dir_names, filenames in os.walk(root_path):
        if ".git" in dir_names:
            git_repos.append(dirpath)
            dir_names.remove(".git")
    logging.info(f"Found {len(git_repos)} Git repositories")
    return git_repos

def get_git_logs(days: int = 1) -> list:
    """
    Returns a list of logs for all Git repositories under root_path.
    :param days:
    :return:
    """
    logging.info(f"Getting git logs for past {days} day(s)")
    list_of_logs_for_all_repos = []
    list_of_repos = get_git_repo_paths(root_path=root_path)
    for repo_path in list_of_repos:
        git_logs_for_single_repo = get_git_logs_for_single_repo(repo_path=repo_path, days=days)
        list_of_logs_for_all_repos.append(git_logs_for_single_repo)
    return list_of_logs_for_all_repos

def get_git_logs_for_single_repo(repo_path: str, days: int = 1) -> str:
    """
    Returns a list of logs for a single Git repository.
    :param repo_path:
    :param days:
    :return:
    """
    logging.info(f"Getting logs for repository.")
    script_path = "git_components/git_connector.sh"
    command = [script_path, "--path", repo_path, "--days", str(days)]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting git logs: {e.stderr}")
        raise e
