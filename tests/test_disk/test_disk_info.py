import pytest
from http import HTTPStatus
from schemas.models import GetInfo

@pytest.mark.parametrize("headers, expected_status", 
                         [
                        ({}, HTTPStatus.OK),
                        ({"Authorization" : None}, HTTPStatus.UNAUTHORIZED)
                          ])
def test_get_info_about_disk(client, headers, expected_status):
    response = client.get_info(expected_status=expected_status, headers=headers)
    if response.status_code == 200:
        info = GetInfo.model_validate(response.json())
        assert info.total_space >= 0
    
