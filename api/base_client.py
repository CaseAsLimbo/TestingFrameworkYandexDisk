import requests

class BaseClient:

    def __init__(self, session: requests.Session, base_url: str, api_version: str, oauth_token: str | None = None, timeout: int = 10):
        self.base_url = base_url
        self.api_version = api_version
        self.timeout = timeout
        self._session = session # создавать и закрывать в фикстуре
        if oauth_token is not None:
            self._session.headers["Authorization"] = f"OAuth {oauth_token}"


    def get(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url.rstrip("/")}/{self.api_version.strip("/")}/{path.lstrip("/")}/"
        return self._session.get(url, timeout=self.timeout, **kwargs)


    def post(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url.rstrip("/")}/{self.api_version.strip("/")}/{path.lstrip("/")}/"
        return self._session.get(url, timeout=self.timeout, **kwargs)


    def put(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url.rstrip("/")}/{self.api_version.strip("/")}/{path.lstrip("/")}/"
        return self._session.get(url, timeout=self.timeout, **kwargs)


    def patch(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url.rstrip("/")}/{self.api_version.strip("/")}/{path.lstrip("/")}/"
        return self._session.get(url, timeout=self.timeout, **kwargs)


    def delete(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url.rstrip("/")}/{self.api_version.strip("/")}/{path.lstrip("/")}/"
        return self._session.get(url, timeout=self.timeout, **kwargs)

