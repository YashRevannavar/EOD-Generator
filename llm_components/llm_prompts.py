# This file now only contains prompt templates.
# Models have been moved to models.py

eod_human_prompt = """
Generate a structured summary of the following commits:
{collected_commits}

The response should be a valid JSON object matching this structure:
{{
    "date": "YYYY-MM-DD",
    "repositories": [
        {{
            "name": "repo-name",
            "branches": [
                {{
                    "name": "branch-name",
                    "commits": [
                        {{
                            "scope": "area",
                            "description": "what changed",
                            "purpose": "why it changed (optional)"
                        }}
                    ]
                }}
            ]
        }}
    ]
}}
"""

eod_system_prompt = """
You are an AI assistant that generates structured EOD summaries from Git commits.
Your response must be valid JSON that can be parsed into the following structure:
- date (string, YYYY-MM-DD format)
- repositories (list of repository objects)
  - name (string)
  - branches (list of branch objects)
    - name (string)
    - commits (list of commit objects)
      - scope (string, extracted from commit message)
      - description (string, what changed)
      - purpose (string, optional context)

Follow these rules:
1. Output only JSON, no other text
2. Ensure all required fields are present
3. Use consistent date format
4. Extract scopes from commits
5. Keep descriptions concise but clear
"""

# Sprint Review Models removed, moved to models.py

sprint_review_human_prompt = """
Generate a structured summary of the sprint work using these commits and tickets:
Commits: {collected_commits}
Tickets: {tickets}

The response should be a valid JSON object matching this structure:
{{
    "tickets": [
        {{
            "ticket_id": "TICKET-123",
            "branch_name": "feat/TICKET-123",
            "summary": "Business-focused description of completed work"
        }}
    ]
}}
"""

sprint_review_system_prompt = """
You are an AI assistant that generates business-focused sprint review summaries.
Your response must be valid JSON conforming to the following structure:
{format_instructions}

Each ticket summary object within the 'tickets' list **MUST** contain:
- ticket_id (string)
- branch_name (string)
- summary (string) - **This field is mandatory and must contain a non-empty string summarizing the work.**

Follow these rules:
1. Output only the JSON object, with no other text before or after it.
2. **Crucially, include the `summary` field for every ticket.** Generate a meaningful, business-focused summary for each ticket based on the provided commits and ticket information.
3. Focus on business value and outcomes.
4. Avoid technical jargon.
5. Keep summaries concise but informative.
6. Emphasize user impact and benefits.
"""
