from requests import Response  # type: ignore

from deps_classification.extras import BaseRESTClient, DEPSTokenAuth
from deps_classification.infrastructure.access_management import user

from .exceptions import RestClientError

__all__ = ["GenericProxy"]


class GenericProxy(BaseRESTClient):
    exception: type[RestClientError]

    def _set_authentication(self) -> None:
        self._session.auth = DEPSTokenAuth(user)

    def _check_response(self, response: Response) -> None:
        if not response.ok:
            self._logger.error(
                "Response to %s with payload %s failed with error %s",
                response.url,
                response.request.__dict__,
                response.content,
            )

            raise self.exception(response.content.decode())
