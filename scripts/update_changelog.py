import datetime as dt
import os
import re
import subprocess
from collections.abc import Iterable
from pathlib import Path

import git
import github.PullRequest
import github.Repository
from github import Github
from jinja2 import Template

CURRENT_FILE = Path(__file__)
ROOT = CURRENT_FILE.parents[1]
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")
GIT_BRANCH = os.getenv("GITHUB_REF_NAME")


def main() -> None:
    try:
        print("Some data", CURRENT_FILE, ROOT, "token yes" if GITHUB_TOKEN else "token no", GITHUB_REPO, GIT_BRANCH)
        repo = Github(login_or_token=GITHUB_TOKEN).get_repo(GITHUB_REPO)
        merged_date = dt.date.today()
        merged_pulls = list(iter_pulls(repo, merged_date))

        if not merged_pulls:
            print("Nothing was merged, existing.")
            return

        to_update = f"{merged_date:%Y.%m.%d}"
        changelog_path = ROOT / "CHANGELOG.md"
        write_changelog(changelog_path, to_update)
        print(f"Wrote {changelog_path}")

        update_git_repo([changelog_path])

        print("end")
    except Exception as ex:
        print("Some exception occurred when reading Github", ex)

def iter_pulls(
    repo: github.Repository.Repository,
    merged_date: dt.date,
) -> Iterable[github.PullRequest.PullRequest]:
    """Fetch merged pull requests at the date we're interested in."""
    recent_pulls = repo.get_pulls(
        state="closed",
        sort="updated",
        direction="desc",
    ).get_page(0)
    for pull in recent_pulls:
        if pull.merged and pull.merged_at.date() == merged_date:
            yield pull

def write_changelog(file_path: Path, content: str) -> None:
    """Write Release details to the changelog file."""
    file_path.write_text(content)

def update_git_repo(paths: list[Path]) -> None:
    """Commit, tag changes in git repo and push to origin."""
    repo = git.Repo(ROOT)
    for path in paths:
        repo.git.add(path)
    message = f"writing to..."

    user = repo.git.config("--get", "user.name")
    email = repo.git.config("--get", "user.email")

    repo.git.commit(
        m=message,
        author=f"{user} <{email}>",
    )
    server = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    print(f"Pushing changes to {GIT_BRANCH} branch of {GITHUB_REPO}")
    repo.git.push(server, GIT_BRANCH)
    # repo.git.push("--tags", server, GIT_BRANCH)

if __name__ == "__main__":
    if GITHUB_REPO is None:
        raise RuntimeError("No github repo, please set the environment variable GITHUB_REPOSITORY")
    if GIT_BRANCH is None:
        raise RuntimeError("No git branch set, please set the GITHUB_REF_NAME environment variable")
    main()