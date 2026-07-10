import pytest
from project_git_release.classes import GitReleasePR

from conftest import create_response, to_bytes
from project_git_release_connector_gitea import GiteaConnector


@pytest.mark.parametrize("case", [None], ids=["Get latest release PR by tag - 404"])
def test_get_release_by_tag_no_release(case, release_config, connector, mock_get):
    mock_get.return_value = create_response(404)

    response = connector.get_release_by_tag("")
    assert response is None


@pytest.mark.parametrize("case", [None], ids=["Get latest release PR by tag - OK"])
def test_get_release_by_tag_has_details(case, mocker, release_config, mock_get, log_info_spy):
    valid_version = "1.0.0"
    valid_tag_message = "Valid version"
    valid_commit_sha = "Does matter"
    gitea_response = {
        "tag_name": valid_version
    }
    tag_details_response = {
        "commit": {
            "sha": valid_commit_sha
        },
        "message": valid_tag_message
    }
    mocker.patch.object(GiteaConnector, "get_tag_details", side_effect=lambda
        tag_name: tag_details_response if tag_name == valid_version else None)
    connector = GiteaConnector(release_config)

    mock_get.return_value = create_response(content=to_bytes(gitea_response))
    response = connector.get_release_by_tag(valid_version)
    assert response is not None
    assert valid_version == response.tag_name
    assert valid_tag_message == response.tag_message
    assert valid_commit_sha == response.commit_sha

    log_info_spy.assert_any_call(f"Found the release by tag {valid_version}")
    log_info_spy.assert_any_call(f"Commit SHA for version {valid_version}: {valid_commit_sha}")


@pytest.mark.parametrize("case", [None],
                         ids=["Get latest release PR by tag - Has tag, but no details"])
def test_get_latest_release_2nd_release_no_details(case, mocker, release_config, mock_get, log_info_spy):
    valid_version = "1.0.0"
    gitea_response = {
        "tag_name": valid_version
    }
    mocker.patch.object(GiteaConnector, "get_tag_details", return_value=None)
    connector = GiteaConnector(release_config)

    mock_get.return_value = create_response(content=to_bytes(gitea_response))
    response = connector.get_release_by_tag(valid_version)
    assert response is None

    log_info_spy.assert_any_call(f"Found the release by tag {valid_version}")
