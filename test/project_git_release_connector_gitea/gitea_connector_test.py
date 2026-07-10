import json

import pytest
from project_git_release.classes import GitReleasePR
from project_git_release.core import ReleaseConfig
from pytest_mock import MockType
from requests import Response

from project_git_release_connector_gitea import GiteaConnector, log

__TEST_TOKEN_VALUE = "VERY_TOKEN_VALUE"
__TEST_REPO_URL = "http://localhost:8080"
__TEST_REPO_OWNER = "owner"
__TEST_REPO_NAME = "repository"
__TEST_DEFAULT_BRANCH = "main"
__TEST_FULL_URL = f"{__TEST_REPO_URL}/{__TEST_REPO_OWNER}/{__TEST_REPO_NAME}"


def create_response(status_code: int = 200, content: bytes | None = None) -> Response:
    return_val = Response()
    return_val.status_code = status_code
    if content is not None:
        return_val._content = content
    return return_val


def to_bytes(content: object) -> bytes:
    return json.dumps(content).encode('utf-8')


@pytest.fixture
def release_config():
    return ReleaseConfig(
        token=__TEST_TOKEN_VALUE,
        url=__TEST_REPO_URL,
        owner=__TEST_REPO_OWNER,
        repo=__TEST_REPO_NAME
    )


@pytest.fixture
def connector(release_config):
    return GiteaConnector(release_config)


@pytest.fixture
def mock_get(mocker):
    return mocker.patch('requests.get')


@pytest.fixture
def mock_post(mocker):
    return mocker.patch('requests.post')


@pytest.fixture
def log_info_spy(mocker):
    return mocker.spy(log, 'info')


@pytest.fixture
def log_debug_spy(mocker) -> MockType:
    return mocker.spy(log, 'debug')


@pytest.fixture
def log_error_spy(mocker) -> MockType:
    return mocker.spy(log, 'error')

@pytest.mark.parametrize("case", [None], ids=["Standard response - 404"])
def test__get_404(case, connector, mock_get, log_info_spy):
    mock_get.return_value = create_response(404)

    response = connector.get_latest_release_pr("open")
    assert response is None
    log_info_spy.assert_any_call(f"No pull requests can be found for repo {__TEST_REPO_NAME}")


@pytest.mark.parametrize("case", [None], ids=["Standard response - 500"])
def test__get_500(case, connector, mock_get, log_error_spy, log_debug_spy):
    test_body = to_bytes({"test": "value"})
    mock_get.return_value = create_response(
        status_code=500,
        content=test_body
    )

    response = connector.get_latest_release_pr("open")
    assert response is None
    log_error_spy.assert_any_call(f"Error while querying the pull requests for repo {__TEST_REPO_NAME}")
    log_debug_spy.assert_any_call(test_body)


@pytest.mark.parametrize("case", [None], ids=["Get latest release PR - OK"])
def test_get_latest_release_pr(case, release_config, connector, mock_get):
    first_test_object = {
        "head": {
            "ref": f"{release_config.release_branch}"
        },
        "state": "open",
        "id": -1,
        "number": -2,
        "title": "very_title",
        "merge_commit_sha": "test_commit_sha",
        "body": "test_comment",
        "merged": True
    }
    test_body = to_bytes([first_test_object])
    mock_get.return_value = create_response(content=test_body)
    response = connector.get_latest_release_pr("open")

    assert response is not None and type(response) == GitReleasePR
    assert first_test_object["id"] == response.id
    assert first_test_object["number"] == response.number
    assert first_test_object["title"] == response.title
    assert first_test_object["merge_commit_sha"] == response.commit_sha
    assert first_test_object["body"] == response.comment
    assert first_test_object["merged"] == response.merged


@pytest.mark.parametrize("case", [None], ids=["Get latest release PR - the latest PR is not release PR - OK"])
def test_get_latest_release_pr_first_is_not_release(case, release_config, connector, mock_get):
    first_test_object = {
        "head": {
            "ref": "very_feature"
        },
        "state": "open"
    }
    second_test_object = {
        "head": {
            "ref": f"{release_config.release_branch}"
        },
        "state": "open",
        "id": -1,
        "number": -2,
        "title": "very_title",
        "merge_commit_sha": "test_commit_sha",
        "body": "test_comment",
        "merged": True
    }
    test_body = to_bytes([first_test_object, second_test_object])
    mock_get.return_value = create_response(content=test_body)
    response = connector.get_latest_release_pr("open")

    assert response is not None and type(response) == GitReleasePR
    assert second_test_object["id"] == response.id
    assert second_test_object["number"] == response.number
    assert second_test_object["title"] == response.title
    assert second_test_object["merge_commit_sha"] == response.commit_sha
    assert second_test_object["body"] == response.comment
    assert second_test_object["merged"] == response.merged


@pytest.mark.parametrize("case", [None], ids=["Get latest release PR - wrong state - OK"])
def test_get_latest_release_pr_wrong_state(case, release_config, connector, mock_get):
    first_test_object = {
        "head": {
            "ref": f"{release_config.default_branch}"
        },
        "state": "closed",
        "id": -1,
        "number": -2,
        "title": "very_title",
        "merge_commit_sha": "test_commit_sha",
        "body": "test_comment",
        "merged": True
    }
    test_body = to_bytes([first_test_object])
    mock_get.return_value = create_response(content=test_body)
    response = connector.get_latest_release_pr("open")

    assert response is None


@pytest.mark.parametrize("case", [None], ids=["Get latest release PRs - OK"])
def test_get_latest_release_prs(case, release_config, connector, mock_get):
    first_test_object = {
        "head": {
            "ref": f"{release_config.release_branch}"
        },
        "state": "open",
        "id": -1,
        "number": -2,
        "title": "very_title_01",
        "merge_commit_sha": "test_commit_sha_01",
        "body": "test_comment_01",
        "merged": True
    }
    second_test_object = {
        "head": {
            "ref": f"{release_config.release_branch}"
        },
        "state": "open",
        "id": -3,
        "number": -4,
        "title": "very_title_02",
        "merge_commit_sha": "test_commit_sha_02",
        "body": "test_comment_02",
        "merged": False
    }
    test_body = to_bytes([first_test_object, second_test_object])
    mock_get.return_value = create_response(content=test_body)
    response = connector.get_latest_release_prs("open")

    assert response is not None
    assert 2 == len(response)

    first_response = response[0]
    assert first_test_object["id"] == first_response.id
    assert first_test_object["number"] == first_response.number
    assert first_test_object["title"] == first_response.title
    assert first_test_object["merge_commit_sha"] == first_response.commit_sha
    assert first_test_object["body"] == first_response.comment
    assert first_test_object["merged"] == first_response.merged

    second_response = response[1]
    assert second_test_object["id"] == second_response.id
    assert second_test_object["number"] == second_response.number
    assert second_test_object["title"] == second_response.title
    assert second_test_object["merge_commit_sha"] == second_response.commit_sha
    assert second_test_object["body"] == second_response.comment
    assert second_test_object["merged"] == second_response.merged


@pytest.mark.parametrize("case", [None], ids=["Get latest release PRs - empty result"])
def test_get_latest_release_prs_empty_result(case, release_config, connector, mock_get):
    test_body = to_bytes([])
    mock_get.return_value = create_response(content=test_body)
    response = connector.get_latest_release_prs("open")

    assert response is not None
    assert 0 == len(response)

@pytest.mark.parametrize("case", [None], ids=["Create PR - OK"])
def test_create_pr(case, release_config, connector, mock_post):
    commit_text = "test_commit_text"
    pr_title = "test_pr_title"
    body = {
        "head": {
            "ref": f"{release_config.release_branch}"
        },
        "state": "open",
        "id": -1,
        "number": -2,
        "title": pr_title,
        "merge_commit_sha": "test_commit_sha",
        "body": commit_text
    }
    test_body = to_bytes(body)
    mock_post.return_value = create_response(content=test_body)
    response = connector.create_release_pr(pr_title, commit_text)

    assert response is not None and type(response) == GitReleasePR
    assert body["id"] == response.id
    assert body["number"] == response.number
    assert body["merge_commit_sha"] == response.commit_sha
    assert pr_title == response.title
    assert commit_text == response.comment
    assert False == response.merged

    service_request = mock_post.call_args[1]['json']
    assert pr_title == service_request['title']
    assert commit_text == service_request['body']
    assert release_config.default_branch == service_request['base']
    assert release_config.release_branch == service_request['head']


@pytest.mark.parametrize("case", [None], ids=["Create PR - 404"])
def test_create_pr_404(case, release_config, connector, mock_post, log_info_spy):
    commit_text = "test_commit_text"
    pr_title = "test_pr_title"

    mock_post.return_value = create_response(404)
    response = connector.create_release_pr(pr_title, commit_text)
    assert response is None
    log_info_spy.assert_any_call(f"No pull requests can be found for repo {release_config.repo}")


@pytest.mark.parametrize("case", [None], ids=["Create PR - 500"])
def test_create_pr_500(case, release_config, connector, mock_post, log_error_spy, log_debug_spy):
    commit_text = "test_commit_text"
    pr_title = "test_pr_title"

    dummy_content = to_bytes({"dummy_content": "content"})
    mock_post.return_value = create_response(500, content=dummy_content)
    response = connector.create_release_pr(pr_title, commit_text)
    assert response is None
    log_error_spy.assert_any_call(f"Error while querying the pull requests for repo {release_config.repo}")
    log_debug_spy.assert_any_call(dummy_content)
