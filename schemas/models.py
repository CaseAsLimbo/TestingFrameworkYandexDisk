from schemas.base import Base


class GetInfo(Base):
    trash_size: int
    total_space: int
    used_space: int
    system_folders: dict

