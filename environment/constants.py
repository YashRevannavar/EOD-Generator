import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
root_path = os.getenv("REPO_PATHS")

list_of_tickets = ["Find a better way to do this"] # TODO: Find a better way to do this