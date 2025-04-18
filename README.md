# EOD Generator

An automated tool that generates End-of-Day (EOD) summaries and Sprint Reviews from Git commit logs using a configurable LLM (defaults to Ollama), with a web interface for easy access.

## Description

EOD Generator scans specified Git repositories, collects commit logs, and uses a Large Language Model (LLM), such as one hosted via Ollama, to generate meaningful summaries of development activities. It offers two main features:

1. **EOD Summary**: Generates daily summaries of development activities across repositories
2. **Sprint Review**: Creates comprehensive sprint review reports by analyzing commits within a date range and correlating them with ticket IDs

The tool features a web interface for easy interaction and real-time summary generation.

## Features

- Web interface for easy access and interaction
- EOD summary generation from Git commits
- Sprint review report generation with ticket correlation
- Support for multiple Git repositories
- Real-time progress updates
- Error handling and logging
- Clean, organized output format

## Prerequisites

- Python 3.x
- Git installed and accessible from command line
- Ollama installed and running locally (or access to another LLM configured via environment variables)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/EOD-Generator.git
cd EOD-Generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with:
```env
# REPO_PATHS is now configured via constants.py, update it there if needed.
# Example for Ollama configuration:
OLLAMA_MODEL="deepseek-coder:6.7b" # Specify the Ollama model to use (e.g., llama3, mistral)
```
   *(Note: The `REPO_PATHS` configuration has been moved to `environment/constants.py`)*

## Usage

Start the web server:
```bash
python main.py
```

Access the web interface at `http://localhost:5001` to:
- Generate EOD summaries with one click
- Create sprint review reports by specifying date ranges and tickets
- View real-time progress updates
- Get formatted, easy-to-read summaries

## Key Components (Refactored Architecture)

The application follows a service-oriented architecture with dependency inversion:

### Core Models (`models.py`)
- Defines Pydantic models for data structures used throughout the application (e.g., `HistoryEntry`, `DailySummary`, `SprintReviewSummary`).

### Service Interfaces (`services/interfaces.py`)
- Defines abstract base classes (ABCs) for core services (`IGitService`, `ILlmService`, `IHistoryService`), establishing contracts for implementations.

### Generation Service (`services/generation_service.py`)
- Orchestrates the EOD and Sprint Review generation process.
- Depends on the service interfaces (`IGitService`, `ILlmService`, `IHistoryService`) via dependency injection.
- Contains the primary business logic for fetching data, calling the LLM, formatting results, and saving history.

### Concrete Service Implementations
- **Git Service (`git_components/git_service.py`)**: Implements `IGitService`. Uses helper shell scripts (`eod_git_connector.sh`, `sprint_review_git_connector.sh`) to fetch Git logs.
- **LLM Service (`llm_components/llm_service.py`)**: Implements `ILlmService`. Interacts with the configured LLM (defaulting to Ollama via LangChain) to generate summaries based on prompts defined in `llm_components/llm_prompts.py`.
- **History Service (`history_components/history_service.py`)**: Implements `IHistoryService`. Manages loading and saving generation history to a JSON file (`data/.history.json`).

### Backend (`main.py`)
- Sets up the Flask web server.
- Defines API endpoints (`/run-eod`, `/run-sprint-review`, history endpoints, etc.).
- Instantiates concrete services and injects them into `GenerationService`.
- Delegates request handling to `GenerationService`.
- Handles streaming responses (Server-Sent Events) for real-time updates.

### Web Interface (`static/`)
- Provides the user interface (HTML, CSS, JavaScript) for interacting with the backend API.

## Output Format

### EOD Summary
```
- Date

- Git Repo Name 1:
- Branch Name:
- (type of commit) Summarized Task 1
- (type of commit) Summarized Task 2

- Git Repo Name 2:
- Branch Name:
- (type of commit) Summarized Task 1
```

### Sprint Review
- Organized by ticket ID
- Non-technical language for stakeholder understanding
- Detailed task descriptions and achievements
- Focus on acceptance criteria completion

## Dependencies

- flask: Web server framework
- flask-cors: Cross-origin resource sharing
- langchain-community: Provides Ollama integration (and potentially others)
- langchain-core: Core LangChain functionality
- python-dotenv: Environment variable management
- pydantic: Data validation and modeling

## Environment Requirements

- Ollama installed and running locally (ensure the desired model is pulled, e.g., `ollama pull deepseek-coder:6.7b`).
- Environment variables (optional, defined in `.env`):
  - `OLLAMA_MODEL`: Specifies the Ollama model to use (defaults if not set).
- Configuration:
  - Update `environment/constants.py` with the correct `root_path` pointing to the directory containing your Git repositories.

## Error Handling

The application includes comprehensive error handling and logging:
- Git operation failures
- LLM processing errors
- AWS authentication issues
- Web server errors
- API endpoint errors

Logs are output with timestamps and appropriate log levels for easy debugging.

## Development

To run in development mode:
```bash
python main.py
```

The server will start in debug mode on port 5001 with hot reloading enabled.