"""Thin wrappers around the GitHub API for use as agent tools.

Each function is designed to be called by an LLM through tool calling.
Every function accepts primitive types (strings, ints, lists) so the LLM
can invoke them, and returns dicts that are easy to serialize.
"""
import os
from typing import Optional
from dotenv import load_dotenv
from github import Github, Auth
from github.GithubException import GithubException

load_dotenv()

_gh_client: Optional[Github] = None


def _client() -> Github:
    """Lazy singleton for the authenticated GitHub client."""
    global _gh_client
    if _gh_client is None:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise RuntimeError("GITHUB_TOKEN not set in .env")
        _gh_client = Github(auth=Auth.Token(token))
    return _gh_client


def get_issue(repo: str, issue_number: int) -> dict:
    """Fetch a single issue's title, body, current labels, and author.

    Args:
        repo: Full repo name in "owner/name" format, e.g. "myuser/agent-sandbox".
        issue_number: The issue number (not the ID).

    Returns:
        Dict with keys: number, title, body, author, current_labels, state, url.
    """
    try:
        r = _client().get_repo(repo)
        issue = r.get_issue(issue_number)
        return {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body or "",
            "author": issue.user.login,
            "current_labels": [l.name for l in issue.labels],
            "state": issue.state,
            "url": issue.html_url,
        }
    except GithubException as e:
        return {"error": f"GitHub API error: {e.data.get('message', str(e))}"}


def list_available_labels(repo: str) -> dict:
    """List all labels that exist in the repo, so the LLM knows what it can use.

    Args:
        repo: Full repo name in "owner/name" format.

    Returns:
        Dict with key "labels": a list of {name, description, color} entries.
    """
    try:
        r = _client().get_repo(repo)
        return {
            "labels": [
                {"name": l.name, "description": l.description or "", "color": l.color}
                for l in r.get_labels()
            ]
        }
    except GithubException as e:
        return {"error": f"GitHub API error: {e.data.get('message', str(e))}"}


def add_labels_to_issue(repo: str, issue_number: int, labels: list[str]) -> dict:
    """Add one or more labels to an issue. Existing labels are preserved.

    Args:
        repo: Full repo name in "owner/name" format.
        issue_number: The issue number.
        labels: List of label names to add. All must already exist on the repo.

    Returns:
        Dict with keys: success, labels_after.
    """
    try:
        r = _client().get_repo(repo)
        issue = r.get_issue(issue_number)
        for label in labels:
            issue.add_to_labels(label)
        issue = r.get_issue(issue_number)    # refresh
        return {
            "success": True,
            "labels_after": [l.name for l in issue.labels],
        }
    except GithubException as e:
        return {"success": False, "error": f"GitHub API error: {e.data.get('message', str(e))}"}


def post_comment(repo: str, issue_number: int, body: str) -> dict:
    """Post a comment on an issue.

    Args:
        repo: Full repo name in "owner/name" format.
        issue_number: The issue number.
        body: Markdown-formatted comment body.

    Returns:
        Dict with keys: success, comment_id, comment_url.
    """
    try:
        r = _client().get_repo(repo)
        issue = r.get_issue(issue_number)
        comment = issue.create_comment(body)
        return {
            "success": True,
            "comment_id": comment.id,
            "comment_url": comment.html_url,
        }
    except GithubException as e:
        return {"success": False, "error": f"GitHub API error: {e.data.get('message', str(e))}"}