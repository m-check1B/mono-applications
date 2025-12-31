"""Shared testing utilities for dependency overrides."""

from typing import Any, List


class DummyQuery:
    def __init__(self, items: List[Any]):
        self._items = items

    def filter(self, *args, **kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def offset(self, *_args, **_kwargs):
        return self

    def order_by(self, *_args, **_kwargs):
        return self

    def count(self) -> int:
        return len(self._items)

    def all(self) -> List[Any]:
        return list(self._items)

    def first(self) -> Any:
        return self._items[0] if self._items else None

    def scalars(self):
        return self


class DummyAsyncResult:
    def __init__(self, records: List[Any]):
        self._records = records

    def scalar(self):
        return self._records[0] if self._records else 0

    def scalars(self):
        class _Scalars:
            def __init__(self, records):
                self._records = records

            def all(self):
                return list(self._records)

        return _Scalars(self._records)

    def fetchall(self):
        return list(self._records)


class DummyAsyncDB:
    """Very small async-compatible DB stub."""

    def __init__(self):
        self._records: List[Any] = []

    async def execute(self, *_args, **_kwargs):
        return DummyAsyncResult(self._records)

    async def commit(self):
        return None

    async def refresh(self, _obj):
        return None

    def add(self, _obj):
        return None


async def override_db():
    """Dependency override for get_db that returns a dummy async DB."""
    yield DummyAsyncDB()

