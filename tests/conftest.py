import uuid
import pytest
from schemas.models import LinkUpload
from http import HTTPStatus

@pytest.fixture
def prepared_source_url(client):
    source_path = "disk:/source_for_upload.txt"
    client.put_upload_file(source_path, b"test content")
    client.publish(source_path)
    response = client.get_download_link(source_path)
    link = LinkUpload.model_validate(response.json())
    yield link.href
    client.unpublish(source_path)
    client.delete(source_path)


@pytest.fixture
def uploaded_copy_path(client):
    """Уникальный путь + гарантированный cleanup даже при падении теста."""
    path = f"uploaded_copy_{uuid.uuid4().hex[:8]}.txt"
    yield path
    try:
        client.delete(path, expected_status=HTTPStatus.NO_CONTENT)
    except AssertionError:
        pass  # файла нет — уже удалён или не создан


@pytest.fixture
def published_file(client, uploaded_file):
    """Публикует файл, снимает с публикации после теста."""
    client.publish(uploaded_file)
    yield uploaded_file
    try:
        client.unpublish(uploaded_file, expected_status=HTTPStatus.OK)
    except AssertionError:
        pass


@pytest.fixture
def uploaded_file(client):
    """Создаёт уникальный файл на Диске, удаляет после теста."""
    path = f"disk:/test_file_{uuid.uuid4().hex[:8]}.txt"
    client.put_upload_file(path, b"test content")
    yield path
    try:
        client.delete(path, expected_status=HTTPStatus.NO_CONTENT)
    except AssertionError:
        pass
