import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_repo_paths() -> list:
    repos = os.getenv("REPO_PATHS")
    return repos.split(",") if repos else []
