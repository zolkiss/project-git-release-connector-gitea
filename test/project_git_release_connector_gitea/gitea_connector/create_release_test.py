import pytest
from project_git_release.classes import GitReleasePR, GitRelease, GitReleaseResponse

from conftest import create_response, to_bytes


@pytest.mark.parametrize("case", [None], ids=["Create Release - 404"])
def test_create_release_404(case, connector, mock_post):
    change_log = "Everything is changed"
    release_param = GitRelease(
        tag_name="0.0.1",
        tag_message="VeryTagMessage",
        commit_sha="VeryCommitSha"
    )

    mock_post.return_value = create_response(404)
    response = connector.create_release(release_param, change_log)
    assert response is None

    call_parameter = mock_post.call_args[1]['json']
    assert call_parameter is not None
    assert release_param.tag_name == call_parameter['name']
    assert release_param.tag_name == call_parameter['tag_name']
    assert release_param.tag_message == call_parameter['tag_message']
    assert release_param.commit_sha == call_parameter['target_commitish']


@pytest.mark.parametrize("case", [None], ids=["Create Release - OK"])
def test_create_release_ok(case, connector, mock_post):
    change_log = "Everything is changed"
    release_param = GitRelease(
        tag_name="0.0.1",
        tag_message="VeryTagMessage",
        commit_sha="VeryCommitSha"
    )

    id_value = -2432342
    mock_post.return_value = create_response(content=to_bytes({
        "tag_name": release_param.tag_name,
        "name": release_param.tag_name,
        "target_commitish": release_param.commit_sha,
        "id": id_value,
        "draft": False,
        "prerelease": False
    }))
    response = connector.create_release(release_param, change_log)
    assert response is not None
    assert type(response) == GitReleaseResponse
    assert id_value == response.id
    assert release_param.tag_name == response.name
    assert release_param.tag_name == response.tag_name
    assert release_param.commit_sha == response.commit_sha
    assert not response.draft
    assert not response.pre_release

    call_parameter = mock_post.call_args[1]['json']
    assert call_parameter is not None
    assert release_param.tag_name == call_parameter['name']
    assert release_param.tag_name == call_parameter['tag_name']
    assert release_param.tag_message == call_parameter['tag_message']
    assert release_param.commit_sha == call_parameter['target_commitish']
