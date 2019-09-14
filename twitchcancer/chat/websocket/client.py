import logging
import re

from autobahn.asyncio.websocket import WebSocketClientProtocol
from typing import Optional

from twitchcancer.config import Config
from twitchcancer.storage.storage import Storage
from twitchcancer.symptom.diagnosis import Diagnosis

logger = logging.getLogger(__name__)

diagnosis = Diagnosis()
storage = Storage()


async def record(parsed):
    # compute points for the message
    points = diagnosis.points(parsed['message'])

    # store cancer records for later
    storage.store(parsed['channel'], points)
    # print(parsed['channel'], points)


class TwitchClient(WebSocketClientProtocol):

    def onOpen(self):  # noqa
        self.sendMessage('CAP REQ :twitch.tv/membership'.encode())
        self.sendMessage('PASS {0}'.format(Config.get("monitor.chat.password").lower()).encode())
        self.sendMessage('NICK {0}'.format(Config.get("monitor.chat.username").lower()).encode())

        for channel in self.channels:
            self.sendMessage('JOIN {0}'.format(channel).encode())
            logger.info("joining %s", channel)

    async def onMessage(self, payload, isBinary: bool):  # noqa
        if isBinary:
            logger.debug("Binary message received: {0} bytes".format(len(payload)))
        else:
            message = payload.decode('utf8')

            # respond to PING
            if message[0:4] == "PING":
                self.sendMessage('PONG :tmi.twitch.tv'.encode())
                logger.debug("PONG-ed")
            # try to parse and record messages
            else:
                parsed = TwitchClient.parse_message(message)
                if parsed:
                    await record(parsed)

    async def join(self, channel: str):
        self.channels.add(channel)
        self.sendMessage('JOIN {0}'.format(channel).encode())
        logger.info("joining %s", channel)

    async def leave(self, channel: str):
        self.channels.remove(channel)
        self.sendMessage('PART {0}'.format(channel).encode())
        logger.info("leaving %s", channel)

    channel_message_re = re.compile(".*? PRIVMSG (#[a-zA-z0-9_]*?) :(.*)")

    @classmethod
    def parse_message(cls, line: str) -> Optional[dict]:
        match = cls.channel_message_re.match(line)

        if not match:
            return None

        return {
            'channel': match.group(1),
            'message': match.group(2).replace('\x01ACTION ', '').replace('\x01', '')
        }
