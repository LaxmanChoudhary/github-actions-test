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
        merged_date = dt.date.today() - dt.timedelta(days=1)
        repo = Github(login_or_token=GITHUB_TOKEN).get_repo(GITHUB_REPO)
        merged_pulls = list(iter_pulls(repo, merged_date))
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


if __name__ == "__main__":
    if GITHUB_REPO is None:
        raise RuntimeError("No github repo, please set the environment variable GITHUB_REPOSITORY")
    if GIT_BRANCH is None:
        raise RuntimeError("No git branch set, please set the GITHUB_REF_NAME environment variable")
    main()