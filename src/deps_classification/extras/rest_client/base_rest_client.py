import logging

import requests

from .adapter import DEPSHTTPSAdapter

__all__ = ["BaseRESTClient"]


class BaseRESTClient:
    def __init__(
        self,
        base_url: str,
    ) -> None:
        self._base_url = base_url

        self._session = requests.Session()
        self._initialize()

        self._logger = logging.getLogger(self.__class__.__name__)

    def _initialize(self) -> None:
        self._mount_adapter()
        self._set_session_headers()
        self._set_authentication()

    def _mount_adapter(self) -> None:
        self._session.mount(self._base_url, DEPSHTTPSAdapter())

    def _set_session_headers(self) -> None:
        pass

    def _set_authentication(self) -> None:
        pass
