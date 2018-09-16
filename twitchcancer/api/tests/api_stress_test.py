import argparse
import asyncio
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory


class APIClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):  # noqa
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):  # noqa
        print("WebSocket connection open.")

        self.sendMessage('{"subscribe": "twitchcancer.live"}'.encode())
        self.sendMessage('{"subscribe": "twitchcancer.leaderboards"}'.encode())
        self.sendMessage('{"subscribe": "twitchcancer.leaderboard.cancer.minute"}'.encode())
        self.sendMessage('{"subscribe": "twitchcancer.status"}'.encode())
        self.sendMessage('{"subscribe": "twitchcancer.channel.forsenlol"}'.encode())

    def onClose(self, wasClean, code, reason):  # noqa
        print("WebSocket connection closed: {0}".format(reason))


async def run(connect, client_per_step, time_between_cycles):
    while True:
        for n in range(client_per_step):
            await connect()
        await asyncio.sleep(time_between_cycles)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', default='127.0.0.1',
                        help="ip of the API (default: 127.0.0.1)")
    parser.add_argument('--port', dest='port', default=8080,
                        help="port of the API (default: 8080)")
    parser.add_argument('--clients', dest='clients', default=100, type=int,
                        help="number of clients to add each cycle")
    parser.add_argument('--duration', dest='duration', default=10, type=int,
                        help="duration of each cycle")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    factory = WebSocketClientFactory()
    factory.protocol = APIClientProtocol

    async def connect():
        print("Connecting...")
        await loop.create_connection(factory, args.host, args.port)

    loop.run_until_complete(run(connect, args.clients, args.duration))
