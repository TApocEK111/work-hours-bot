from dataclasses import dataclass

from domain.models.entity import Entity


@dataclass
class User(Entity):
    name: str

    def __post_init__(self):
        if self.id is None:
            raise ValueError("User must be initialized with id")
