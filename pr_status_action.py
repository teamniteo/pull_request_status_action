import json
import logging
import os
import time
import typing as t
from dataclasses import dataclass
from enum import Enum, auto

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pr_status_action")


class States(Enum):
    """Commit states supported by Github."""

    pending = "pending"
    success = "success"
    failure = "failure"
    error = "error"


@dataclass(frozen=True)
class Args:
    """User input arguments."""

    repository: str
    pr_num: int
    context: str
    state: States
    target_url: t.Optional[str]
    description: t.Optional[str]


def _headers() -> t.Dict[str, str]:
    """Headers for Github API calls."""

    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
    }


def _get_statuses_url(repository: str, pr_num: int) -> str:
    """Get Pull Request's Status URL.
    
        Ref: https://docs.github.com/en/rest/reference/pulls#get-a-pull-request

    Inputs:
        repository: Owner and name of the Repository.
        pr_num: Pull Request Number.
    
    Output:
        Status URL of the latest commit.
    """

    url = f"https://api.github.com/repos/{repository}/pulls/{pr_num}"

    response = requests.get(url, headers=_headers())
    response.raise_for_status()

    response_json = response.json()
    return response_json["statuses_url"]


def _create_commit_status(statuses_url: str, args: Args) -> None:
    """Update a commit status to mark PR state.
    
        Ref: https://docs.github.com/en/rest/reference/repos#create-a-commit-status

    Inputs:
        statuses_url: Statuses URL of the latest commit.
        args: User inputs.
    """

    payload = {"state": args.state.value, "context": args.context}

    if args.target_url:
        payload["target_url"] = args.target_url

    if args.description:
        payload["description"] = args.description

    response = requests.post(statuses_url, headers=_headers(), data=json.dumps(payload))
    response.raise_for_status()


def main() -> None:
    """Main workflow.
    
    All the inputs are received from workflow as environment variables.
    """

    args = Args(
        repository=os.environ["INPUT_REPOSITORY"],
        pr_num=int(os.environ["INPUT_PR_NUMBER"]),
        context=os.environ["INPUT_CONTEXT"],
        state=States(os.environ["INPUT_STATE"]),
        target_url=os.environ.get("INPUT_TARGET_URL"),
        description=os.environ.get("INPUT_DESCRIPTION"),
    )
    statuses_url = _get_statuses_url(args.repository, args.pr_num)

    _create_commit_status(statuses_url, args)

    logger.info(
        f"Status of the #{args.pr_num} PR has been changed to {args.state.value} state."
    )


if __name__ == "__main__":  # pragma: no cover
    main()
