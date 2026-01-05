from adp.services.observer.base_observer import BaseObserver

class QueueTarget(BaseObserver):
    """Target save to S3 and send message to Queue."""

    def __init__(self, queue_url: str, aws_credentials: dict = None):
        self.queue_url = queue_url
        self.aws_credentials = aws_credentials or {}

    async def push(self, data: dict) -> None:
        """
        Asynchronously send data to the configured Queue.
        """
        # code here
        pass