from schemas.models import GetInfo
from api.routes.disk_routes import DiskInfoRouter
from pydantic import TypeAdapter

class DiskClient:

    def __init__(self, base_client):
        self._client = base_client

    
    def get_info(self):
        response = self._client.get(DiskInfoRouter.INFO)
        adapter = TypeAdapter(GetInfo)
        return adapter.validate_python(response)

