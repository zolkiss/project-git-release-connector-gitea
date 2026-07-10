import pytest
from project_git_release.classes import GitReleasePR

from conftest import create_response, to_bytes
from project_git_release_connector_gitea import GiteaConnector


@pytest.mark.parametrize("case", [None], ids=["Get latest release PR - No releases at all"])
def test_get_latest_release_no_release(case, release_config, connector, mock_get):
    mock_get.return_value = create_response(404)

    response = connector.get_latest_release()
    assert response is None


@pytest.mark.parametrize("case", [None], ids=["Get latest release PR - One release with invalid version"])
def test_get_latest_release_no_valid_release(case, release_config, connector, mock_get, log_info_spy):
    version = "small-little-tag"
    response = {
        "tag_name": version
    }
    mock_get.return_value = create_response(content=to_bytes([response]))

    response = connector.get_latest_release()
    assert response is None
    log_info_spy.assert_any_call(
        f"{version} is not a valid SEMVER version (including prefix '{release_config.release_version_prefix}'). Validating the next one...")
    log_info_spy.assert_any_call("There is no release with valid version number.")


@pytest.mark.parametrize("case", [None], ids=["Get latest release PR - One release with invalid version"])
def test_get_latest_release_2nd_release_valid(case, mocker, release_config, mock_get, log_info_spy):
    invalid_version = "small_little_version"
    valid_version = "1.0.0"
    response_one = {
        "tag_name": invalid_version
    }
    valid_tag_message = "Valid version"
    valid_commit_sha = "Does matter"
    response_two = {
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

    mock_get.return_value = create_response(content=to_bytes([response_one, response_two]))
    response = connector.get_latest_release()
    assert response is not None
    assert valid_version == response.tag_name
    assert valid_tag_message == response.tag_message
    assert valid_commit_sha == response.commit_sha

    log_info_spy.assert_any_call(
        f"{invalid_version} is not a valid SEMVER version (including prefix '{release_config.release_version_prefix}'). Validating the next one...")
    log_info_spy.assert_any_call(f"Commit SHA for version {valid_version}: {valid_commit_sha}")
    log_info_spy.assert_any_call(
        f"The {valid_version} tag is a valid SEMVER version with prefix '{release_config.release_version_prefix}'")


@pytest.mark.parametrize("case", [None],
                         ids=["Get latest release PR - One release with invalid version, other has no details"])
def test_get_latest_release_2nd_release_no_details(case, mocker, release_config, mock_get, log_info_spy):
    invalid_version = "small_little_version"
    valid_version = "1.0.0"
    response_one = {
        "tag_name": invalid_version
    }
    response_two = {
        "tag_name": valid_version
    }
    mocker.patch.object(GiteaConnector, "get_tag_details", return_value=None)
    connector = GiteaConnector(release_config)

    mock_get.return_value = create_response(content=to_bytes([response_one, response_two]))
    response = connector.get_latest_release()
    assert response is None

    log_info_spy.assert_any_call(
        f"{invalid_version} is not a valid SEMVER version (including prefix '{release_config.release_version_prefix}'). Validating the next one...")
    log_info_spy.assert_any_call(
        f"The {valid_version} tag is a valid SEMVER version with prefix '{release_config.release_version_prefix}'")
