"""Internal immutable values; no filesystem or process dependencies."""
from dataclasses import dataclass


class InputError(Exception):
    def __init__(self, code: str, pointer: str | None = ""):
        self.code = code
        self.pointer = pointer
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class Page:
    request_cursor: str | None
    ids: tuple[str, ...]
    next_cursor: str | None


@dataclass(frozen=True, slots=True)
class Mutation:
    type: str
    id: str


@dataclass(frozen=True, slots=True)
class Trace:
    snapshot: tuple[str, ...]
    page_size: int
    events: tuple[Page | Mutation, ...]


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    pointer: str
    id: str | None = None
