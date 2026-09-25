"""Tool declarations for Gemini function calling.

Each entry mirrors a function in github_tools.py. Descriptions here are what
the LLM actually reads when deciding whether to call a tool, so they need to
be clear and specific.
"""
from google.genai import types
from src import github_tools

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_issue",
            "description": "Fetch a GitHub issue's title, body, author, current labels, and state.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Full repo name, 'owner/name'."},
                    "issue_number": {"type": "integer", "description": "The issue number."},
                },
                "required": ["repo", "issue_number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_available_labels",
            "description": "List all labels that exist in the repo. Call before adding labels.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Full repo name, 'owner/name'."},
                },
                "required": ["repo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_labels_to_issue",
            "description": "Add labels to an issue. Labels must already exist in the repo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Full repo name, 'owner/name'."},
                    "issue_number": {"type": "integer", "description": "The issue number."},
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of label names to add.",
                    },
                },
                "required": ["repo", "issue_number", "labels"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "post_comment",
            "description": "Post a Markdown comment on a GitHub issue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Full repo name, 'owner/name'."},
                    "issue_number": {"type": "integer", "description": "The issue number."},
                    "body": {"type": "string", "description": "Markdown comment body."},
                },
                "required": ["repo", "issue_number", "body"],
            },
        },
    },
]



TOOL_REGISTRY = {
    "get_issue": github_tools.get_issue,
    "list_available_labels": github_tools.list_available_labels,
    "add_labels_to_issue": github_tools.add_labels_to_issue,
    "post_comment": github_tools.post_comment,
}


