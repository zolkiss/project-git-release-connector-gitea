import pytest
from project_git_release.classes import GitReleasePR

from conftest import create_response, to_bytes


@pytest.mark.parametrize("case", [None], ids=["Update PR - OK"])
def test_update_pr(case, release_config, connector, mock_patch):
    commit_text = "new_test_commit_text"
    pr_title = "new_test_pr_title"
    pr_number = -32424

    body = {
        "head": {
            "ref": f"{release_config.release_branch}"
        },
        "state": "open",
        "id": -1,
        "number": pr_number,
        "title": pr_title,
        "merge_commit_sha": "test_commit_sha",
        "body": commit_text
    }

    test_body = to_bytes(body)
    mock_patch.return_value = create_response(content=test_body)
    response = connector.update_release_pr(pr_number, pr_title, commit_text)

    assert response is not None and type(response) == GitReleasePR
    assert body["id"] == response.id
    assert body["number"] == response.number
    assert body["merge_commit_sha"] == response.commit_sha
    assert pr_title == response.title
    assert commit_text == response.comment
    assert False == response.merged

    service_request = mock_patch.call_args[1]['data']
    assert pr_title == service_request['title']
    assert commit_text == service_request['body']


@pytest.mark.parametrize("case", [None], ids=["Update PR - 404"])
def test_update_pr_404(case, release_config, connector, mock_patch, log_info_spy):
    commit_text = "test_commit_text"
    pr_title = "test_pr_title"
    pr_number = -23243214

    mock_patch.return_value = create_response(404)
    response = connector.update_release_pr(pr_number, pr_title, commit_text)
    assert response is None
    log_info_spy.assert_any_call(f"No pull requests can be found for repo {release_config.repo}")


@pytest.mark.parametrize("case", [None], ids=["Update PR - 500"])
def test_update_pr_500(case, release_config, connector, mock_patch, log_error_spy, log_debug_spy):
    commit_text = "test_commit_text"
    pr_title = "test_pr_title"
    pr_number = -1212342

    dummy_content = to_bytes({"dummy_content": "content"})
    mock_patch.return_value = create_response(500, content=dummy_content)
    response = connector.update_release_pr(pr_number, pr_title, commit_text)
    assert response is None
    log_error_spy.assert_any_call(f"Error while querying the pull requests for repo {release_config.repo}")
    log_debug_spy.assert_any_call(dummy_content)
