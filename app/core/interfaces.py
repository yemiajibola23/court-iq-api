from typing import Protocol, runtime_checkable

class StorageClient(Protocol):
    """Core application interfaces and abstract protocols."""

    def delete_blob(self, path: str) -> None: ...