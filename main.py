from git_components.git_service import get_git_logs
from environment.constants import get_repo_paths
from llm_components.llm_connector import llm_summary_generator

def collect_git_logs(days) -> list:
    repos = get_repo_paths()
    logs = get_git_logs(repo_paths=repos, days=days)
    return logs


if __name__ == "__main__":
    logs = collect_git_logs(days=2)
    responses = llm_summary_generator(collected_commits=logs)
    print(f"Responses: {responses}")