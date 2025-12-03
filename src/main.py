import os
from pprint import pprint

from jira_api import add_release_to_issue, get_or_create_release, mark_release_as_released
from notes_parser import extract_changes, extract_issue_id, extract_issue_ids_from_commits

print("=" * 60)
print(f"Release to JIRA Action")
print("=" * 60)

# Get repository name from GITHUB_REPOSITORY (format: owner/repo)
github_repository = os.environ.get("GITHUB_REPOSITORY", "")
library_name = github_repository.split("/")[-1] if github_repository else "unknown"

release_name = os.environ["GITHUB_REF_NAME"]
is_pre_release = os.environ.get("IS_PRE_RELEASE", "false").lower() == "true"

# Prefix release name with library name
release_name = f"{library_name} {release_name}"

if is_pre_release:
    release_name = f"{release_name} (pre-release)"

mark_released = os.environ.get("INPUT_JIRA_MARK_RELEASED", "false").lower() == "true"
print(f"\n📦 Processing release: {release_name}")
print(f"   Library: {library_name}")
print(f"   Mark as released: {mark_released}")

release = get_or_create_release(release_name)
print(f"✓ JIRA Release created/found: {release.get('name')} (ID: {release.get('id')})")

# Collect issue IDs from both PR titles and commit messages
issue_ids = set()

# Extract from PR titles (existing functionality)
print("\n" + "-" * 60)
print("🔍 Scanning PR titles from release notes...")
print("-" * 60)
changes = extract_changes()
print(f"Found {len(changes)} PRs in release notes")

pr_issue_ids = []
for change in changes:
    issue_id = extract_issue_id(change["title"])
    if issue_id:
        pr_issue_ids.append(issue_id)
        issue_ids.add(issue_id)
        print(f"  ✓ {issue_id} from PR: {change['title'][:60]}...")
    else:
        print(f"  - No issue ID in: {change['title'][:60]}...")

print(f"\n📋 Issues from PRs: {len(pr_issue_ids)} issue(s)")
if pr_issue_ids:
    print(f"   {', '.join(sorted(set(pr_issue_ids)))}")

# Extract from commit messages (new functionality)
print("\n" + "-" * 60)
print("🔍 Scanning commit messages...")
print("-" * 60)
commit_issue_ids = extract_issue_ids_from_commits()
print(f"Found {len(commit_issue_ids)} issue ID(s) in commit messages")
if commit_issue_ids:
    for issue_id in sorted(commit_issue_ids):
        print(f"  ✓ {issue_id}")
    issue_ids.update(commit_issue_ids)
else:
    print("  - No issue IDs found in commits")

# Update all found issues
print("\n" + "=" * 60)
print(f"📊 Summary: {len(issue_ids)} unique issue(s) found")
print("=" * 60)
if issue_ids:
    for issue_id in sorted(issue_ids):
        print(f"  • {issue_id}")
else:
    print("  No issues to update")

print("\n" + "-" * 60)
print("🔄 Updating JIRA issues...")
print("-" * 60)
success_count = 0
for issue_id in sorted(issue_ids):
    try:
        print(f"  Updating {issue_id}...", end=" ")
        add_release_to_issue(release_name, issue_id)
        print("✓")
        success_count += 1
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print(f"✅ Complete: {success_count}/{len(issue_ids)} issue(s) updated successfully")
print("=" * 60)

# Mark release as released if requested
if mark_released:
    print("\n" + "-" * 60)
    print("🏁 Marking release as released...")
    print("-" * 60)
    try:
        mark_release_as_released(release.get('id'))
        print(f"✓ Release {release_name} marked as released")
    except Exception as e:
        print(f"✗ Failed to mark release as released: {e}")
