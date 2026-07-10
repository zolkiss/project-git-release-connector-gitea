import json

import pytest
from project_git_release.core import ReleaseConfig
from pytest_mock import MockType
from requests import Response

from project_git_release_connector_gitea import log, GiteaConnector

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
def mock_patch(mocker):
    return mocker.patch('requests.patch')


@pytest.fixture
def log_info_spy(mocker):
    return mocker.spy(log, 'info')


@pytest.fixture
def log_debug_spy(mocker) -> MockType:
    return mocker.spy(log, 'debug')


@pytest.fixture
def log_error_spy(mocker) -> MockType:
    return mocker.spy(log, 'error')
