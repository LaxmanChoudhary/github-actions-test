import os
from pathlib import Path

from github import Github

CURRENT_FILE = Path(__file__)
ROOT = CURRENT_FILE.parents[1]
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")
GIT_BRANCH = os.getenv("GITHUB_REF_NAME")


def main() -> None:
    try:
        print("Some data", CURRENT_FILE, ROOT, "token yes" if GITHUB_TOKEN else "token no", GITHUB_REPO, GIT_BRANCH)
        repo = Github(login_or_token=GITHUB_TOKEN).get_repo(GITHUB_REPO)
    except Exception as ex:
        print("Some exception occurred when reading Github", ex)


if __name__ == "__main__":
    if GITHUB_REPO is None:
        raise RuntimeError("No github repo, please set the environment variable GITHUB_REPOSITORY")
    if GIT_BRANCH is None:
        raise RuntimeError("No git branch set, please set the GITHUB_REF_NAME environment variable")
    main()