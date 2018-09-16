import logging
from autobahn.asyncio.websocket import WebSocketClientFactory

from twitchcancer.chat.websocket.client import TwitchClient

logger = logging.getLogger(__name__)


class TwitchClientFactory(WebSocketClientFactory):
    protocol = TwitchClient

    def __init__(self, *args, **kwargs):
        self.client = None
        WebSocketClientFactory.__init__(self, *args, **kwargs)

    def __call__(self):
        proto = self.protocol()
        proto.factory = self
        proto.channels = set()

        self.client = proto
        logger.debug('created a client for server %s', self.server)
        return proto

    async def join(self, channel):
        await self.client.join(channel)

    async def leave(self, channel):
        await self.client.leave(channel)

    def __getattr__(self, attr):
        if attr == "channels":
            return self.client.channels
