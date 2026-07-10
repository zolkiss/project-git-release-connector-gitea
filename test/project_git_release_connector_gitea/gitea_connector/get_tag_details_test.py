import pytest
from project_git_release.classes import GitReleasePR

from conftest import create_response, to_bytes


@pytest.mark.parametrize("case", [None], ids=["Get tag details - 404"])
def test_get_tag_details_404(case, connector, mock_get, log_info_spy):
    mock_get.return_value = create_response(404)

    response = connector.get_tag_details("")
    assert response is None


@pytest.mark.parametrize("case", [None], ids=["Get tag details - OK"])
def test_get_tag_details(case, connector, mock_get, log_error_spy, log_debug_spy):
    body_content = {
        "dummy_key": "dummy_value"
    }
    get_details_response = to_bytes(body_content)
    valid_tag = "0.0.1"
    mock_get.return_value = create_response(content=get_details_response)
    details = connector.get_tag_details(valid_tag)
    assert body_content == details
