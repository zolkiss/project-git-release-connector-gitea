from project_git_release.core import ReleaseConfig
from project_git_release_connector_gitea import GiteaConnector


def test_dummy_test():
    release_config = ReleaseConfig(token="", url="dummy_url", owner="dummy_owner", repo="dummy_repo")
    connector = GiteaConnector(release_config)
    assert True
