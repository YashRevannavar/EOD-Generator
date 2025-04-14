# EOD Generator

An automated tool that generates End-of-Day (EOD) summaries and Sprint Reviews from Git commit logs using AWS Bedrock's Claude 3 LLM, with a web interface for easy access.

## Description

EOD Generator scans specified Git repositories, collects commit logs, and uses AWS Bedrock's Claude 3 to generate meaningful summaries of development activities. It offers two main features:

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
- AWS account with Bedrock access
- AWS credentials configured locally

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
REPO_PATHS="/path/to/your/repositories"  # Directory containing Git repositories to scan
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_aws_region
```

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

## Key Components

### Backend (`main.py`)
- Flask web server setup
- API endpoints for EOD and Sprint Review generation
- Real-time progress updates using server-sent events
- Error handling and logging

### Git Service (`git_components/git_service.py`)
- `get_git_logs()`: Collects commit logs from all repositories
- `get_git_logs_by_date_range()`: Retrieves logs for specific date ranges
- `get_git_logs_for_single_repo()`: Retrieves logs from a single repository

### LLM Connector (`llm_components/llm_connector.py`)
- `get_llm_bedrock_ai()`: Initializes AWS Bedrock Claude 3 client
- `llm_eod_summary_generator()`: Processes git logs for daily summaries
- `llm_sprint_review_summary_generator()`: Generates sprint review reports

### Web Interface (`static/`)
- Clean, intuitive user interface
- Real-time progress updates
- Support for both EOD and Sprint Review generation

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
- langchain-aws: AWS Bedrock integration
- python-dotenv: Environment variable management
- langchain-core: Core LangChain functionality

## Environment Requirements

- AWS Bedrock enabled in your AWS account
- Proper IAM permissions for Bedrock access
- Environment variables:
  - REPO_PATHS
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_REGION

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