import pytest
from project_git_release.classes import GitReleasePR, GitHashAndMsg

from conftest import create_response, to_bytes


@pytest.mark.parametrize("case", [None], ids=["Get commit details - 404"])
def test_get_commit_details_404(case, connector, mock_get, log_info_spy):
    mock_get.return_value = create_response(404)

    response = connector.get_commit_details(GitHashAndMsg(hash="EpicHash", message="VeryMessage"))
    assert response is None


@pytest.mark.parametrize("case", [None], ids=["Get commit details - One line message"])
def test_get_commit_details_one_line_message(case, connector, mock_get, log_info_spy):
    message = "VeryMessage"
    detail_message = "VeryDetailedStuff"
    hash = "VeryHash"
    created = "2025-01-01T00:00:00"
    commit_detail_content = {
        "commit": {
            "message": f"    {message}  {detail_message}     "
        },
        "created": created
    }
    mock_get.return_value = create_response(content=to_bytes(commit_detail_content))

    response = connector.get_commit_details(GitHashAndMsg(hash=hash, message=message))
    assert response is not None
    assert message == response.title
    assert hash == response.hash
    assert created == response.creation_time.isoformat()
    assert detail_message == response.body
    assert [] == response.footers


@pytest.mark.parametrize("case", [None], ids=["Get commit details - Multi line message"])
def test_get_commit_details_multi_line(case, connector, mock_get, log_info_spy):
    message = "VeryMessage"
    detail_message = "VeryDetailedStuff"
    hash = "VeryHash"
    created = "2025-01-01T00:00:00"
    footer_one = "VeryFooterOne"
    footer_two = "Not that very footer\nbut multiline"
    commit_detail_content = {
        "commit": {
            "message": f"    {message}  {detail_message}  \n\n{footer_one}\n\n{footer_two}"
        },
        "created": created
    }
    mock_get.return_value = create_response(content=to_bytes(commit_detail_content))

    response = connector.get_commit_details(GitHashAndMsg(hash=hash, message=message))
    assert response is not None
    assert message == response.title
    assert hash == response.hash
    assert created == response.creation_time.isoformat()
    assert detail_message == response.body
    assert 2 == len(response.footers)
    assert footer_one == response.footers[0]
    assert footer_two == response.footers[1]
