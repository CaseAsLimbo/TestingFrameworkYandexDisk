import pytest
import requests
from config.settings import get_settings
from api.base_client import BaseClient
from api.clients.disk_client import DiskClient

@pytest.fixture(scope="session")
def settings():
    """Получение настроек из класса Settings."""
    return get_settings()

@pytest.fixture(scope="session")
def session_factory():
    """Фабрика сессий типа requests.Session."""
    sessions = []

    def _make_session(**kwargs) -> requests.Session:
        _session = requests.Session(**kwargs)
        sessions.append(_session)
        return _session

    yield _make_session

    for session in sessions:
        session.close()


@pytest.fixture(scope="session")
def base_client(settings, session_factory):
    """
    Создание базового клиента. По умолчанию базовый клиент
    создается с OAuth-токеном, заголовок авторизации отключается
    для методов не требующих таковую (большинство требуют авторизацию).
    """
    return BaseClient(
            session_factory(), 
            settings.base_url,
            settings.api_version, 
            settings.api_token
        )


@pytest.fixture(scope="session")
def client(base_client):
    """Создание кастомного клиента, реализующего API-методы."""
    return DiskClient(base_client)


