from http import HTTPStatus

import pytest

from schemas.models import GetInfo, LinkUpload, Resource


@pytest.mark.parametrize(
    "headers, expected_status",
    [({}, HTTPStatus.OK), ({"Authorization": None}, HTTPStatus.UNAUTHORIZED)],
)
def test_get_info_about_disk(client, headers, expected_status):
    response = client.get_info(expected_status=expected_status, headers=headers)
    if response.status_code == 200:
        info = GetInfo.model_validate(response.json())
        assert info.total_space >= 0


class TestPostUploadFromUrl:
    """Тесты для POST /v1/disk/resources/upload (загрузка по URL)."""

    def test_upload_from_url_success(
        self, client, prepared_source_url, uploaded_copy_path
    ):
        """Полный цикл: POST - polling - GET meta. Файл скопирован по URL."""
        target_path = uploaded_copy_path

        response = client.post_upload_from_url(target_path, prepared_source_url)

        assert response.status_code == HTTPStatus.OK
        meta = Resource.model_validate(response.json())
        assert meta.name == target_path
        assert meta.type == "file"
        assert meta.size == len(b"test content")

        client.delete(target_path)

    def test_upload_from_url_returns_202_with_link(self, client, prepared_source_url):
        """Raw-метод: POST возвращает 202 и Link с href для polling."""
        target_path = "disk:/uploaded_copy.txt"

        response = client.post_upload_from_url_raw(target_path, prepared_source_url)

        assert response.status_code == HTTPStatus.ACCEPTED
        link = LinkUpload.model_validate(response.json())
        assert link.method == "GET"
        assert link.href.startswith("https://")

        # Завершаем асинхронную операцию и убираем за собой
        client._wait_polling(link.href)
        client.delete(target_path)

    def test_upload_from_url_unauthorized(self, client, prepared_source_url):
        """POST без токена - 401."""
        client.post_upload_from_url_raw(
            "disk:/x.txt",
            prepared_source_url,
            headers={"Authorization": None},
            expected_status=HTTPStatus.UNAUTHORIZED,
        )

    @pytest.mark.parametrize(
        "url",
        [
            "not-a-url",
            "http://",
            "",
        ],
    )
    def test_upload_from_url_invalid_url(self, client, url):
        """POST с невалидным URL - 400."""
        client.post_upload_from_url_raw(
            "disk:/x.txt",
            url,
            expected_status=HTTPStatus.BAD_REQUEST,
        )

    def test_upload_from_url_parent_not_found(self, client, prepared_source_url):
        """POST в несуществующую папку - 409 (семантически должно быть 404, но сервис отдает 409)."""
        client.post_upload_from_url_raw(
            "disk:/no-such-folder-xyz/file.txt",
            prepared_source_url,
            expected_status=HTTPStatus.CONFLICT,
        )

    def test_upload_from_url_async_failure(self, client):
        """POST с URL, который сервер не может скачать - операция failed при polling."""
        response = client.post_upload_from_url_raw(
            "disk:/unreachable.txt",
            "https://nonexistent-domain-xyz.invalid/file.txt",
        )
        assert response.status_code == HTTPStatus.ACCEPTED

        link = LinkUpload.model_validate(response.json())

        with pytest.raises(AssertionError, match="failed"):
            client._wait_polling(link.href, timeout=30)


class TestGetMeta:
    """Тесты для GET /v1/disk/resources."""

    def test_get_meta_success(self, client, uploaded_file):
        """Метаинформация о существующем файле - 200 + Resource."""
        response = client.get_meta(uploaded_file)

        assert response.status_code == HTTPStatus.OK
        meta = Resource.model_validate(response.json())
        assert meta.name == uploaded_file.rsplit("/", 1)[-1]
        assert meta.type == "file"
        assert meta.size == len(b"test content")

    def test_get_meta_not_found(self, client):
        """Несуществующий путь - 404."""
        client.get_meta(
            "disk:/no-such-file-xyz.txt",
            expected_status=HTTPStatus.NOT_FOUND,
        )

    def test_get_meta_unauthorized(self, client, uploaded_file):
        """Без токена - 401."""
        client.get_meta(
            uploaded_file,
            headers={"Authorization": None},
            expected_status=HTTPStatus.UNAUTHORIZED,
        )

    def test_get_meta_returns_correct_name(self, client, uploaded_file):
        """Ответ содержит имя, соответствующее запрошенному пути."""
        response = client.get_meta(uploaded_file)
        meta = Resource.model_validate(response.json())

        expected_name = uploaded_file.rsplit("/", 1)[-1]
        assert meta.name == expected_name
        assert meta.path.endswith(expected_name)


class TestDelete:
    """Тесты для DELETE /v1/disk/resources."""

    def test_delete_success(self, client, uploaded_file):
        """Удаление существующего файла - 204 No Content."""
        response = client.delete(uploaded_file)
        assert response.status_code == HTTPStatus.NO_CONTENT

    def test_delete_removes_resource(self, client, uploaded_file):
        """После удаления get_meta - 404 (побочный эффект проверен)."""
        client.delete(uploaded_file)
        client.get_meta(uploaded_file, expected_status=HTTPStatus.NOT_FOUND)

    def test_delete_not_found(self, client):
        """Удаление несуществующего файла - 404."""
        client.delete(
            "disk:/no-such-file-xyz.txt",
            expected_status=HTTPStatus.NOT_FOUND,
        )

    def test_delete_unauthorized(self, client, uploaded_file):
        """Без токена - 401."""
        client.delete(
            uploaded_file,
            headers={"Authorization": None},
            expected_status=HTTPStatus.UNAUTHORIZED,
        )


class TestPublish:
    """Тесты для PUT /v1/disk/resources/publish и /unpublish."""

    def test_publish_success(self, client, uploaded_file):
        """Публикация файла - 200 + Link на публичный ресурс."""
        response = client.publish(uploaded_file)

        assert response.status_code == HTTPStatus.OK
        link = LinkUpload.model_validate(response.json())
        assert link.method == "GET"
        assert link.href.startswith("https://")

        # cleanup — снимаем с публикации
        client.unpublish(uploaded_file)

    def test_publish_not_found(self, client):
        """Публикация несуществующего файла - 404."""
        client.publish(
            "disk:/no-such-file-xyz.txt",
            expected_status=HTTPStatus.NOT_FOUND,
        )

    def test_publish_unauthorized(self, client, uploaded_file):
        """Без токена - 401."""
        client.publish(
            uploaded_file,
            headers={"Authorization": None},
            expected_status=HTTPStatus.UNAUTHORIZED,
        )

    def test_unpublish_success(self, client, published_file):
        """Снятие с публикации - 200."""
        response = client.unpublish(published_file)
        assert response.status_code == HTTPStatus.OK

    def test_published_resource_has_download_link(self, client, published_file):
        """Опубликованный файл доступен по прямой ссылке скачивания."""
        response = client.get_download_link(published_file)

        assert response.status_code == HTTPStatus.OK
        link = LinkUpload.model_validate(response.json())
        assert link.href.startswith("https://")
