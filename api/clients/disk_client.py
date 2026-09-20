import time
from http import HTTPStatus

from requests import Response

from api.routes.disk_routes import DiskUploadRouter
from schemas.models import LinkUpload


class DiskClient:
    def __init__(self, base_client):
        self._client = base_client

    def get_info(
        self, expected_status: HTTPStatus = HTTPStatus.OK, **kwargs
    ) -> Response:
        response = self._client.get(DiskUploadRouter.INFO, **kwargs)
        self._expected(response, expected_status)
        return response

    def get_meta(
        self,
        path: str,
        fields: list | None = None,
        limit: int | None = None,
        offset: int | None = None,
        preview_crop: bool | None = None,
        preview_size: str | None = None,
        sort: str | None = None,
        expected_status: HTTPStatus = HTTPStatus.OK,
        **kwargs,
    ):
        dict_of_params = {
            "path": path,
            "fields": ",".join(fields) if fields is not None else None,
            "limit": limit,
            "offset": offset,
            "preview_crop": str(preview_crop).lower()
            if preview_crop is not None
            else None,
            "preview_size": preview_size,
            "sort": sort,
        }
        query = {k: v for k, v in dict_of_params.items() if v is not None}
        response = self._client.get(DiskUploadRouter.RESOURCES, params=query, **kwargs)
        self._expected(response, expected_status)
        return response

    def post_upload_from_url(
        self,
        path: str,
        url: str,
        disable_redirects: bool | None = None,
        fields: list[str] | None = None,
        expected_status: HTTPStatus = HTTPStatus.ACCEPTED,
        **kwargs,
    ) -> Response:
        """POST полный путь: POST запрос - polling - GET meta."""
        dict_of_params = {
            "path": path,
            "url": url,
            "disable_redirects": str(disable_redirects).lower()
            if disable_redirects is not None
            else None,
            "fields": ",".join(fields) if fields is not None else None,
        }
        query = {k: v for k, v in dict_of_params.items() if v is not None}

        link_response = self._client.post(
            DiskUploadRouter.UPLOAD, params=query, **kwargs
        )
        self._expected(link_response, expected_status=expected_status)
        link_model = LinkUpload.model_validate(link_response.json())
        self._wait_polling(link_model.href)
        return self.get_meta(path)

    def post_upload_from_url_raw(
        self,
        path: str,
        url: str,
        disable_redirects: bool | None = None,
        fields: list[str] | None = None,
        expected_status: HTTPStatus = HTTPStatus.ACCEPTED,
        **kwargs,
    ) -> Response:
        """POST, останавливаемся на шаге получения url для загрузки для проверки ассинхронности."""
        dict_of_params = {
            "path": path,
            "url": url,
            "disable_redirects": str(disable_redirects).lower()
            if disable_redirects is not None
            else None,
            "fields": ",".join(fields) if fields is not None else None,
        }
        query = {k: v for k, v in dict_of_params.items() if v is not None}

        link_response = self._client.post(
            DiskUploadRouter.UPLOAD, params=query, **kwargs
        )
        self._expected(link_response, expected_status)
        return link_response

    def put_upload_file(
        self,
        path: str,
        content: bytes,
        overwrite: bool = True,
        fields: list[str] | None = None,
        expected_status: HTTPStatus = HTTPStatus.CREATED,
        **kwargs,
    ) -> Response:
        """
        Загружает файл на Диск.
        Полный цикл: запрос URL для загрузки -> загрузка файла по этому URL.

        :param path: Путь на Диске, куда загрузить файл (например, "/disk:/source.txt").
        :param content: Бинарное содержимое файла.
        :param overwrite: Перезаписывать ли существующий файл.
        """
        dict_of_params = {
            "path": path,
            "overwrite": str(overwrite).lower(),
            "fields": ",".join(fields) if fields is not None else None,
        }
        query = {k: v for k, v in dict_of_params.items() if v is not None}

        response = self._client.get(DiskUploadRouter.UPLOAD, params=query, **kwargs)

        self._expected(response, HTTPStatus.OK)

        link = LinkUpload.model_validate(response.json())
        upload_response = self._put_absolute(link.href, data=content)
        self._expected(upload_response, expected_status)

        return upload_response

    def publish(
        self,
        path: str,
        fields: list[str] | None = None,
        public_settings: dict | None = None,
        expected_status: HTTPStatus = HTTPStatus.OK,
        **kwargs,
    ) -> Response:
        """
        Публикует ресурс (файл или папку) и делает его доступным по прямой ссылке.

        :param path: Путь к ресурсу на Диске.
        """

        dict_of_params = {
            "path": path,
            "fields": ",".join(fields) if fields is not None else None,
        }
        query = {k: v for k, v in dict_of_params.items() if v is not None}
        json_body = {
            "public_settings": public_settings if public_settings is not None else {}
        }
        response = self._client.put(
            DiskUploadRouter.PUBLISH, params=query, json=json_body, **kwargs
        )
        self._expected(response, expected_status)
        return response

    def unpublish(
        self,
        path: str,
        fields: list[str] | None = None,
        expected_status: HTTPStatus = HTTPStatus.OK,
        **kwargs,
    ) -> Response:
        """
        Приватизирует ресурс (файл или папку), если он был опубликован.

        :param path: Путь к ресурсу на Диске.
        """
        dict_of_params = {
            "path": path,
            "fields": ",".join(fields) if fields is not None else None,
        }
        query = {k: v for k, v in dict_of_params.items() if v is not None}
        response = self._client.put(DiskUploadRouter.UNPUBLISH, params=query, **kwargs)
        self._expected(response, expected_status)
        return response

    def get_download_link(
        self,
        path: str,
        fields: list[str] | None = None,
        expected_status: HTTPStatus = HTTPStatus.OK,
        **kwargs,
    ) -> Response:
        """
        Запрашивает URL для скачивания файла с Диска.

        :param path: Путь к файлу на Диске.
        :param fields: Какие поля вернуть. Если None — вернутся все.
        """
        dict_of_params = {
            "path": path,
            "fields": ",".join(fields) if fields is not None else None,
        }
        query = {k: v for k, v in dict_of_params.items() if v is not None}

        response = self._client.get(DiskUploadRouter.DOWNLOAD, params=query, **kwargs)
        self._expected(response, expected_status)
        return response

    def delete(
        self,
        path: str,
        permanently: bool = False,
        expected_status: HTTPStatus = HTTPStatus.NO_CONTENT,
        **kwargs,
    ) -> Response:
        """
        Удаляет файл или папку.
        Без permanently — в корзину (204). С permanently=true — навсегда.
        """
        dict_of_params = {
            "path": path,
            "permanently": str(permanently).lower() if permanently else None,
        }
        query = {k: v for k, v in dict_of_params.items() if v is not None}
        response = self._client.delete(
            DiskUploadRouter.RESOURCES, params=query, **kwargs
        )
        self._expected(response, expected_status)
        return response

    def _put_absolute(self, url: str, **kwargs) -> Response:
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = None
        return self._client._session.put(url, headers=headers, **kwargs)

    def _get_absolute(self, url: str, **kwargs) -> Response:
        return self._client._session.get(url, timeout=self._client.timeout, **kwargs)

    def _expected(self, response: Response, expected_status: HTTPStatus) -> None:
        if response.status_code != expected_status:
            raise AssertionError(
                f"Ожидался {expected_status}, получен {response.status_code}. "
                f"URL: {response.url}. Body: {response.text}"
            )

    def _wait_polling(
        self,
        href: str,
        expected_status: HTTPStatus = HTTPStatus.OK,
        poll_interval: float = 1.0,
        timeout: float = 120.0,
    ) -> None:
        start = time.time()
        while time.time() - start < timeout:
            response = self._get_absolute(href)
            self._expected(response, expected_status)
            status = response.json().get("status")

            if status == "success":
                return
            elif status == "failed":
                raise AssertionError(f"POST запрос завершился ошибкой! {response.text}")
            time.sleep(poll_interval)
        raise TimeoutError(f"Операция не завершилась за {timeout} секунд")
