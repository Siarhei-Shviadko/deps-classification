import uuid
from typing import Any, Dict, Generic, Optional, TypeVar

T = TypeVar("T")


class FakeMessage:
    def __init__(self, headers: Dict[str, str] = None, payload: bytes = b""):
        self._headers = headers or {}
        self._payload = payload
        self._headers.setdefault("ID", str(uuid.uuid4()))

    @property
    def payload(self) -> bytes:
        return self._payload

    @property
    def headers(self) -> Dict[str, Any]:
        return self._headers

    def get_id(self) -> str:
        return self._headers.get("ID", "")

    def get_header(self, name: str) -> Optional[str]:
        return self._headers.get(name)

    def get_required_header(self, name: str) -> str:
        if name not in self._headers:
            raise KeyError(f"Required header {name} not found")
        return self._headers[name]

    def has_header(self, name: str) -> bool:
        return name in self._headers

    def set_header(self, name: str, value: str) -> None:
        self._headers[name] = value

    def remove_header(self, name: str) -> None:
        if name in self._headers:
            del self._headers[name]


class EventMessageHeaders:
    AGGREGATE_TYPE = "AGGREGATE_TYPE"
    EVENT_TYPE = "EVENT_TYPE"
    TENANT_ID = "TENANT_ID"
