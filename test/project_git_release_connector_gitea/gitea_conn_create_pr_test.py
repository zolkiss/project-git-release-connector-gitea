import pytest
from project_git_release.classes import GitReleasePR

from conftest import create_response, to_bytes


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
