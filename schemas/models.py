from datetime import datetime

from schemas.base import Base


class GetInfo(Base):
    trash_size: int
    total_space: int
    used_space: int
    system_folders: dict


class LinkUpload(Base):
    href: str
    method: str
    templated: bool


class Resource(Base):
    """Метаинформация о файле или папке на Яндекс.Диске."""

    name: str
    path: str
    type: str
    size: int | None = None
    created: datetime
    modified: datetime
    md5: str | None = None
    mime_type: str | None = None
    media_type: str | None = None
    resource_id: str | None = None
    revision: int | None = None
    custom_properties: dict | None = None
