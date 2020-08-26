import json
import os
import unittest
from unittest import mock
from requests import exceptions

import pytest
import responses
from requests import exceptions

import pr_status_action


@mock.patch.dict(os.environ, {"GITHUB_TOKEN": "secret"})
def test_headers():

    result = pr_status_action._headers()

    assert result == {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token secret",
    }


def test_headers_failures():

    with pytest.raises(KeyError) as excinfo:
        pr_status_action._headers()

    assert "GITHUB_TOKEN" in str(excinfo.value)


@responses.activate
@mock.patch.dict(os.environ, {"GITHUB_TOKEN": "secret"})
def test_get_statuses_url():

    response_body = {"statuses_url": "https://api.github.com/statuses/123"}
    responses.add(
        responses.GET,
        "https://api.github.com/repos/foo/bar/pulls/123",
        status=200,
        body=json.dumps(response_body),
    )

    url = pr_status_action._get_statuses_url("foo/bar", 123)

    assert url == "https://api.github.com/statuses/123"
    assert len(responses.calls) == 1
    assert (
        responses.calls[0].request.headers["Accept"] == "application/vnd.github.v3+json"
    )
    assert responses.calls[0].request.headers["Authorization"] == "token secret"


@responses.activate
@mock.patch.dict(os.environ, {"GITHUB_TOKEN": "secret"})
def test_get_statuses_url_failure():

    responses.add(
        responses.GET, "https://api.github.com/repos/foo/bar/pulls/123", status=404,
    )

    with pytest.raises(exceptions.HTTPError) as excinfo:
        url = pr_status_action._get_statuses_url("foo/bar", 123)

    assert "404 Client Error" in str(excinfo.value)


@responses.activate
@mock.patch.dict(os.environ, {"GITHUB_TOKEN": "secret"})
def test_create_commit_status():

    from pr_status_action import Args

    args = Args(
        repository="foo/bar",
        pr_num=32,
        context="default",
        state=pr_status_action.States.pending,
        target_url="https://foo.com",
        description="Foo",
    )

    responses.add(responses.POST, "https://api.github.com/statuses/123", status=200)

    pr_status_action._create_commit_status("https://api.github.com/statuses/123", args)

    assert len(responses.calls) == 1
    assert (
        responses.calls[0].request.headers["Accept"] == "application/vnd.github.v3+json"
    )
    assert responses.calls[0].request.headers["Authorization"] == "token secret"
    assert (
        responses.calls[0].request.body
        == '{"state": "pending", "context": "default", "target_url": "https://foo.com", "description": "Foo"}'
    )


@responses.activate
@mock.patch.dict(os.environ, {"GITHUB_TOKEN": "secret"})
def test_create_commit_status_with_target_url():

    from pr_status_action import Args

    responses.add(responses.POST, "https://api.github.com/statuses/123", status=200)

    args = Args(
        repository="foo/bar",
        pr_num=32,
        context="default",
        state=pr_status_action.States.pending,
        target_url="https://foo.com",
        description=None,
    )

    pr_status_action._create_commit_status("https://api.github.com/statuses/123", args)

    assert len(responses.calls) == 1
    assert (
        responses.calls[0].request.headers["Accept"] == "application/vnd.github.v3+json"
    )
    assert responses.calls[0].request.headers["Authorization"] == "token secret"


@responses.activate
@mock.patch.dict(os.environ, {"GITHUB_TOKEN": "secret"})
def test_create_commit_status_failure():

    from pr_status_action import Args

    responses.add(responses.POST, "https://api.github.com/statuses/123", status=404)

    args = Args(
        repository="foo/bar",
        pr_num=32,
        context="default",
        state=pr_status_action.States.pending,
        target_url="https://foo.com",
        description=None,
    )

    with pytest.raises(exceptions.HTTPError) as excinfo:
        pr_status_action._create_commit_status(
            "https://api.github.com/statuses/123", args
        )

    assert "404 Client Error" in str(excinfo.value)


@mock.patch.dict(
    os.environ,
    {
        "GITHUB_TOKEN": "secret",
        "INPUT_REPOSITORY": "foo/bar",
        "INPUT_PR_NUMBER": "123",
        "INPUT_CONTEXT": "default",
        "INPUT_STATE": "success",
        "INPUT_TARGET_URL": "http://foo.bar",
        "INPUT_DESCRIPTION": "Foo description",
    },
)
@responses.activate
def test_main_success(caplog):

    response_body = {"statuses_url": "https://api.github.com/statuses/123"}
    responses.add(
        responses.GET,
        "https://api.github.com/repos/foo/bar/pulls/123",
        status=200,
        body=json.dumps(response_body),
    )
    responses.add(responses.POST, "https://api.github.com/statuses/123", status=200)

    pr_status_action.main()

    assert len(responses.calls) == 2
    assert len(caplog.records) == 1
    assert (
        caplog.records[0].message
        == "Status of the #123 PR has been changed to success state."
    )


@mock.patch.dict(
    os.environ,
    {
        "GITHUB_TOKEN": "secret",
        "INPUT_REPOSITORY": "foo/bar",
        "INPUT_PR_NUMBER": "123",
        "INPUT_CONTEXT": "default",
        "INPUT_STATE": "unknown",
    },
)
@responses.activate
def test_main_unknown_state(caplog):

    response_body = {"statuses_url": "https://api.github.com/statuses/123"}
    responses.add(
        responses.GET,
        "https://api.github.com/repos/foo/bar/pulls/123",
        status=200,
        body=json.dumps(response_body),
    )
    responses.add(responses.POST, "https://api.github.com/statuses/123", status=200)

    with pytest.raises(ValueError) as excinfo:
        pr_status_action.main()

    assert "'unknown' is not a valid States" in str(excinfo.value)


@mock.patch.dict(
    os.environ,
    {
        "GITHUB_TOKEN": "secret",
        "INPUT_REPOSITORY": "foo/bar",
        "INPUT_PR_NUMBER": "123",
        "INPUT_CONTEXT": "default",
        "INPUT_STATE": "pending",
    },
)
@responses.activate
def test_main_failure(caplog):

    response_body = {"statuses_url": "https://api.github.com/statuses/123"}
    responses.add(
        responses.GET,
        "https://api.github.com/repos/foo/bar/pulls/123",
        status=503,
        body=json.dumps(response_body),
    )
    responses.add(responses.POST, "https://api.github.com/statuses/123", status=200)

    with pytest.raises(exceptions.HTTPError) as excinfo:
        pr_status_action.main()

    assert "503 Server Error:" in str(excinfo.value)
