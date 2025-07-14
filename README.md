# Pull Request Status Action

[![CircleCI](https://circleci.com/gh/teamniteo/pull_request_status_action/tree/master.svg?style=svg)](https://circleci.com/gh/teamniteo/pull_request_status_action)
[![GitHub marketplace](https://img.shields.io/badge/marketplace-heroku--pull--request--status--action-blue?style=flat-square&logo=github)](https://github.com/marketplace/actions/pull-request-status-action)

A Github Action that creates a `Status` for the Pull Request.

## Usage

```yaml

jobs:
  update-pr-status:
    runs-on: ubuntu-latest
    steps:
    - name: Set PR Status to pending
        uses: teamniteo/pull_request_status_action@v1.0.0
        with:
          # Pull Request number (Mandatory)
          pr_number: 32

          # State to apply (Mandatory)
          # Any of the (error | failure | pending | success) states
          state: pending

          # Name of the repository in {organization}/{repo_name} format (Mandatory)
          repository: teamniteo/the-awesome-repo

          # Name to identify the Status (Optional)
          # Defaults to `default`
          context: default

          # The target URL to associate with the Status (Optional)
          # This URL will be linked from the Github UI to allow users to easily see the source of the status.
          target_url: https://example.target_url.com

          # A short description of the status (Optional)
          description: "An example description"

        env:
          # Default Github Token
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

> `GITHUB_TOKEN` is required to communicate with Github Deployment API. Default token provided by Github can be used.

## Local Development

- Create a Python virtual environment(version > 3.6).
- Activate the environment.
- Install the development dependencies:

```bash
    pip install -r requirements-dev.txt
```

- Make changes.
- Test the changes:

```bash
    make tests
```

- Make sure that coverage is 100%.

## We're hiring!

At Niteo we regularly contribute back to the Open Source community. If you do too, we'd like to invite you to [join our team](https://niteo.co/careers)!
