from dataclasses import dataclass, field


@dataclass
class Entity:
    id: int | None = field(default=None, kw_only=True, repr=False)
