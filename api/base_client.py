import requests
from tenacity import retry, retry_if_exception_type, retry_if_result, stop_after_attempt, wait_exponential
from api.hooks import request_response_logger


def retryable_status(response):
    "True, если ответ сервера в указанному диапазоне кодов: для ретраев."
    return response.status_code in (429, 500, 503, 504, 502)

class BaseClient:

    def __init__(self, _session: requests.Session, base_url: str, api_version: str, oauth_token: str | None = None, timeout: int = 10):
        self.base_url = base_url
        self.api_version = api_version
        self.timeout = timeout
        self._session = _session # создавать и закрывать в фикстуре

        if request_response_logger not in self._session.hooks["response"]:
            self._session.hooks["response"].append(request_response_logger)

        # Заголовки по умолчанию.
        self._session.headers["Accept"] = "application/json"
        self._session.headers["Content-Type"] = "application/json"

        if oauth_token is not None:
            self._session.headers["Authorization"] = f"OAuth {oauth_token}" # отключать выборочно для публичных методов - большинство требуют авторизации, поэтому вкючаем по умолчанию.
    
    def _build_url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}/{self.api_version.strip('/')}/{path.lstrip('/')}" 


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=2, max=10, multiplier=1),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)) | retry_if_result(retryable_status)
            )
    def get(self, path: str, **kwargs) -> requests.Response:
        url = self._build_url(path)
        return self._session.get(url, timeout=self.timeout, **kwargs)


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=2, max=10, multiplier=1),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError))
            )
    def post(self, path: str, **kwargs) -> requests.Response:
        url = self._build_url(path)
        return self._session.post(url, timeout=self.timeout, **kwargs)


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=2, max=10, multiplier=1),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)) | retry_if_result(retryable_status)
            )
    def put(self, path: str, **kwargs) -> requests.Response:
        url = self._build_url(path)
        return self._session.put(url, timeout=self.timeout, **kwargs)


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=2, max=10, multiplier=1),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError))
            )
    def patch(self, path: str, **kwargs) -> requests.Response:
        url = self._build_url(path)
        return self._session.patch(url, timeout=self.timeout, **kwargs)


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=2, max=10, multiplier=1),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)) | retry_if_result(retryable_status)
            )
    def delete(self, path: str, **kwargs) -> requests.Response:
        url =  self._build_url(path)
        return self._session.delete(url, timeout=self.timeout, **kwargs)

