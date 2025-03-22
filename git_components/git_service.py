def get_git_logs(repo_paths: list, days: int = 1) -> list:
    list_of_logs_for_all_repos = []
    for repo_path in repo_paths:
        git_logs_for_single_repo = get_git_logs_for_single_repo(repo_path=repo_path, days=days)
        list_of_logs_for_all_repos.append(git_logs_for_single_repo)
    return list_of_logs_for_all_repos


def get_git_logs_for_single_repo(repo_path: str, days: int = 1) -> str:
    import subprocess

    script_path = "git_components/git_connector.sh"
    command = [script_path, "--path", repo_path, "--days", str(days)]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("❌ Error occurred:")
        print(e.stderr)
        return ""