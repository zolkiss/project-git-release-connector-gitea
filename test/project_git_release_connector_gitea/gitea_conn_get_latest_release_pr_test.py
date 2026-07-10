import pytest
from project_git_release.classes import GitReleasePR

from conftest import create_response, to_bytes, __TEST_REPO_NAME


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


@pytest.mark.parametrize("case", [None], ids=["Get latest release PRs - No response"])
def test_get_latest_release_prs_no_response(case, release_config, connector, mock_get):
    mock_get.return_value = create_response(404)
    response = connector.get_latest_release_prs("open")

    assert response is not None
    assert 0 == len(response)


@pytest.mark.parametrize("case", [None], ids=["Get latest release PRs - empty result"])
def test_get_latest_release_prs_empty_result(case, release_config, connector, mock_get):
    test_body = to_bytes([])
    mock_get.return_value = create_response(content=test_body)
    response = connector.get_latest_release_prs("open")

    assert response is not None
    assert 0 == len(response)
