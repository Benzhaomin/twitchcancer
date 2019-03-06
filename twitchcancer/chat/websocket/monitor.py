import asyncio
import logging
import random
from typing import Optional

from twitchcancer.chat.monitor import Monitor
from twitchcancer.chat.websocket.factory import TwitchClientFactory
from twitchcancer.utils.twitchapi import TwitchApi

logger = logging.getLogger(__name__)


class AsyncWebSocketMonitor(Monitor):

    def __init__(self, viewers=1000):
        super().__init__(viewers)

        self.loop = asyncio.get_event_loop()
        self.clients = {}

    def __getattr__(self, attr):
        if attr == "channels":
            return [channel for client in self.clients.values() for channel in client.channels]

    def run(self):
        """ Join and leave channels, forever
        """
        self.loop.run_until_complete(self.mainloop())

    async def mainloop(self):
        while True:
            await self.autojoin()

            logger.info("Monitor main loop ran with %s clients and %s channels over %s viewers up",
                        len(self.clients), len(self.channels), self.viewers)

            await asyncio.sleep(60)

    async def connect(self, server: str):
        # don't connect twice to the same server
        if server in self.clients:
            return

        logger.info("connecting to %s", server)

        (ip, port) = server.split(":")
        factory = TwitchClientFactory(loop=self.loop)
        factory.loop = self.loop
        factory.server = server

        self.clients[server] = factory

        await self.loop.create_connection(factory, ip, port)

    async def join(self, channel):
        # don't join the same channel twice
        if channel in self.channels:
            # logger.debug("not re-joining %s", channel)
            return

        # get a random client hosting this channel
        server = self.find_server(channel)

        # connect to new clients
        await self.connect(server)

        # join the channel
        logger.debug("will join %s on %s", channel, server)
        await self.clients[server].join(channel)

    async def leave(self, channel):
        # don't leave a channel we didn't join
        if channel not in self.channels:
            # logger.debug("not leaving un-joined channel %s", channel)
            return

        # tell the client to leave the channel
        logger.debug("will leave channel %s", channel)
        client = self.get_client(channel)
        await client.leave(channel)

    async def autojoin(self):
        """ Join any channel over n viewers
        Leave any channel under n viewers (including offline ones)
        """
        # synchronous HTTP request, fine because we'd sleep otherwise
        data = TwitchApi.stream_list()
        if not data:
            # ignore the error, we'll try again next cycle
            return

        # leave any channel out of the top 100 (offline or just further down the list)
        online_channels = ['#' + stream['channel']['name'] for stream in data['streams']]

        for channel in self.channels:
            if channel not in online_channels:
                await self.leave(channel)

        # join channels over n viewers, leave channels under n viewers
        for stream in data['streams']:
            if stream['viewers'] > self.viewers:
                await self.join('#' + stream['channel']['name'])
            else:
                await self.leave('#' + stream['channel']['name'])

    def find_server(self, channel: str) -> str:
        """ Find a server hosting a chat channel
        """
        # TODO: apparently Twitch only exposes a single WS server to the internet, we can just use that and be done
        # properties = TwitchApi.chat_properties(channel)
        # return random.choice(properties['web_socket_servers'])
        return 'irc-ws.chat.twitch.tv:80'

    def get_client(self, channel: str) -> Optional[TwitchClientFactory]:
        """ Returns the client connected to the server where a channel was joined
        """
        for client in self.clients.values():
            if channel in client.channels:
                return client
        return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

    monitor = AsyncWebSocketMonitor()
    monitor.run()
