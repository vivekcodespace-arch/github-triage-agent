import os
from dotenv import load_dotenv
from github import Github, Auth

load_dotenv()

token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("GITHUB_TOKEN not set in .env")

auth = Auth.Token(token)
gh = Github(auth=auth)

user = gh.get_user()
print(f"Authenticated as: {user.login}")
print(f"Public repos: {user.public_repos}")

repo = gh.get_repo("dubinc/dub")
print(f"\nRecent open issues in {repo.full_name}:")
issue_count = 0
for issue in repo.get_issues(state="open"):
    if issue.pull_request:
        continue
        
    labels = [l.name for l in issue.labels]
    print(f"  #{issue.number}: {issue.title[:60]}")
    print(f"    labels: {labels}")
    
    # Increment the counter and break once we hit 5
    issue_count += 1
    if issue_count == 5:
        break

gh.close()