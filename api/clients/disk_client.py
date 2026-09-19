from http import HTTPStatus
from api.routes.disk_routes import DiskInfoRouter
from requests import Response

class DiskClient:

    def __init__(self, base_client):
        self._client = base_client

    
    def get_info(self, expected_status: HTTPStatus = HTTPStatus.OK, **kwargs):
        response = self._client.get(DiskInfoRouter.INFO, **kwargs)
        self._expected(response, expected_status)
        return response
    
    def _expected(self, response: Response, expected_status: HTTPStatus):
        if response.status_code != expected_status:
            raise AssertionError(
                            f"Ожидался {expected_status}, получен {response.status_code}. "        
                            f"URL: {response.url}. Body: {response.text[:300]}"
                    )
