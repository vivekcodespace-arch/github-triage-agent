"""Tests for github_tools.py. These hit the real GitHub API against your sandbox repo.

Set SANDBOX_REPO in your .env, e.g. SANDBOX_REPO=yourusername/agent-sandbox.
"""
import os
import pytest
from dotenv import load_dotenv
from src.github_tools import (
    get_issue,
    list_available_labels,
    add_labels_to_issue,
    post_comment,
)

load_dotenv()

SANDBOX = os.getenv("SANDBOX_REPO")
if not SANDBOX:
    pytest.skip("SANDBOX_REPO not set", allow_module_level=True)


def test_get_issue_returns_expected_fields():
    result = get_issue(SANDBOX, 1)
    assert "error" not in result, result
    assert result["number"] == 1
    assert isinstance(result["title"], str)
    assert isinstance(result["current_labels"], list)


def test_get_issue_nonexistent_returns_error():
    result = get_issue(SANDBOX, 999999)
    assert "error" in result


def test_list_available_labels_returns_defaults():
    result = list_available_labels(SANDBOX)
    assert "error" not in result, result
    label_names = [l["name"] for l in result["labels"]]
    # GitHub creates these by default on every new repo
    assert "bug" in label_names
    assert "enhancement" in label_names


def test_add_labels_and_verify():
    result = add_labels_to_issue(SANDBOX, 1, ["bug"])
    assert result.get("success"), result
    assert "bug" in result["labels_after"]


def test_post_comment_returns_url():
    result = post_comment(SANDBOX, 1, "Test comment from automated test.")
    assert result.get("success"), result
    assert result["comment_url"].startswith("https://github.com/")