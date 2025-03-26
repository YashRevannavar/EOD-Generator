# EOD Generator

An automated tool that generates End-of-Day (EOD) summaries from Git commit logs using AWS Bedrock's Claude 3 LLM.

## Description

EOD Generator scans specified Git repositories, collects commit logs from the past day (configurable), and uses AWS Bedrock's Claude 3 to generate meaningful summaries of the development activities. This tool is perfect for teams wanting to automate their daily progress reports or developers needing to track their work across multiple repositories.


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
pip install langchain-aws python-dotenv
```

3. Create a `.env` file in the root directory with:
```env
REPO_PATHS="/path/to/your/repositories"  # Directory containing Git repositories to scan
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_aws_region
```

## Usage

Run the generator:
```bash
python main.py
```

The tool will:
1. Scan all Git repositories in the specified directory
2. Collect commit logs from the past 24 hours
3. Generate a summary using AWS Bedrock's Claude 3
4. Output the summary to the console

### Custom Time Range

To get logs for a different time range, modify the days parameter in `main.py`:

```python
logs = get_git_logs(days=7)  # Get logs for the past week
```

## Key Components

### Git Service (`git_components/git_service.py`)
- `get_git_repo_paths()`: Recursively finds Git repositories
- `get_git_logs()`: Collects commit logs from all repositories
- `get_git_logs_for_single_repo()`: Retrieves logs from a single repository

### LLM Connector (`llm_components/llm_connector.py`)
- `get_llm_bedrock_ai()`: Initializes AWS Bedrock Claude 3 client
- `llm_summary_generator()`: Processes git logs and generates summaries

## Dependencies

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

Logs are output with timestamps and appropriate log levels for easy debugging.