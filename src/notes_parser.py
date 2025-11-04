import os
import re

PROJECT = os.environ["INPUT_JIRA_PROJECT"]
ISSUE_PATTERN = rf"{PROJECT}-[0-9]+"
CHANGES_SECTION = "What's Changed"


def _get_section(md_content, section_title):
    return md_content.split(f"## {section_title}\n", 1)[1].split("\n\n", 1)[0]


def _parse_changelist(content):
    items = []
    for line in content.split("\n"):
        line = line[2:]
        try:
            pr_title, line = line.split(" by @", 1)
            author, pr_link = line.split(" in ", 1)
            items.append(
                {
                    "title": pr_title,
                    "author": author,
                    "link": pr_link,
                }
            )
        except Exception as ex:
            print('skipped', line, ex)
    return items


def extract_changes():
    with open("notes.md", "r") as f:
        content = f.read()

    if CHANGES_SECTION not in content:
        return []

    return _parse_changelist(_get_section(content, CHANGES_SECTION))


def extract_issue_id(change):
    matches = re.findall(ISSUE_PATTERN, change)
    if not matches:
        return None
    return matches[0]


def extract_issue_ids_from_commits():
    """Extract all Jira issue IDs from commit messages."""
    issue_ids = set()
    
    try:
        with open("commits.txt", "r") as f:
            content = f.read()
        
        if not content.strip():
            print("  ⚠ commits.txt is empty")
            return []
        
        matches = re.findall(ISSUE_PATTERN, content)
        issue_ids.update(matches)
    except FileNotFoundError:
        print("  ⚠ No commits.txt file found")
    
    return list(issue_ids)
