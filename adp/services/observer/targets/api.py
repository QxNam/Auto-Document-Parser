from adp.services.observer.base_observer import BaseObserver

class HttpTarget(BaseObserver):
    """Target HTTP send data async, support auth, retry, rate_limit."""

    def __init__(self, url: str, auth: dict = None, headers: dict = None):
        self.url = url
        self.auth = auth
        self.headers = headers or {}

    async def push(self, data: dict) -> None:
        """
        Asynchronously send data to the configured HTTP endpoint.
        """
        # code here
        pass
