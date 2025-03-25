from git_components.git_service import get_git_logs
from llm_components.llm_connector import llm_summary_generator

if __name__ == "__main__":
    logs = get_git_logs(days=1)
    responses = llm_summary_generator(collected_commits=logs)
    print(f"Responses: \n {responses}")
