import json

import pytest
from project_git_release.core import ReleaseConfig
from pytest_mock import MockType
from requests import Response

from project_git_release_connector_gitea import GiteaConnector, log

__TEST_TOKEN_VALUE = "VERY_TOKEN_VALUE"
__TEST_REPO_URL = "http://localhost:8080"
__TEST_REPO_OWNER = "owner"
__TEST_REPO_NAME = "repository"
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
def log_info_spy(mocker):
    return mocker.spy(log, 'info')


@pytest.fixture
def log_debug_spy(mocker) -> MockType:
    return mocker.spy(log, 'debug')


@pytest.fixture
def log_error_spy(mocker) -> MockType:
    return mocker.spy(log, 'error')


def test__get_404(mocker, connector, mock_get, log_info_spy):
    mock_get.return_value = create_response(404)

    response = connector.get_latest_release_pr("open")
    assert response is None
    log_info_spy.assert_any_call(f"No pull requests can be found for repo {__TEST_REPO_NAME}")


def test__get_500(mocker, connector, mock_get, log_error_spy, log_debug_spy):
    test_body = to_bytes({"test": "value"})
    mock_get.return_value = create_response(
        status_code=500,
        content=test_body
    )

    response = connector.get_latest_release_pr("open")
    assert response is None
    log_error_spy.assert_any_call(f"Error while querying the pull requests for repo {__TEST_REPO_NAME}")
    log_debug_spy.assert_any_call(test_body)
