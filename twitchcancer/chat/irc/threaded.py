import time
import logging
import random
from threading import Thread

from twitchcancer.chat.irc.irc import IRC, ServerConfigurationError, ServerConnectionError
from twitchcancer.chat.monitor import Monitor
from twitchcancer.storage.storage import Storage
from twitchcancer.symptom.diagnosis import Diagnosis
from twitchcancer.utils.twitchapi import TwitchApi

logger = logging.getLogger(__name__)


class ThreadedIRCMonitor(Monitor):

    def __init__(self, viewers):
        super().__init__(viewers)

        self.storage = Storage()
        self.diagnosis = Diagnosis()
        self.clients = {}

    # fake a channels property, extracted from clients
    def __getattr__(self, attr):
        if attr == "channels":
            return [channel for client in self.clients.values() for channel in client.channels]

    # run the main thread, it'll auto add channels and mainly sleep
    def run(self):
        try:
            while True:
                self.autojoin()

                logger.info("cycle ran with %s clients and %s channels over %s viewers up", len(self.clients),
                            len(self.channels), self.viewers)

                # wait until our next cycle
                time.sleep(60)
        except KeyboardInterrupt:
            pass

    # returns a client connected to the given host or None on failures
    def connect(self, host):
        try:
            # don't connect to the same server twice
            if host in self.clients:
                return self.clients[host]

            # ignore buggy host:port
            if host is None or ":" not in host:
                return None

            # create an IRC client and connect to the server right away
            (ip, port) = host.split(":")
            client = IRC(ip, port)
            client.connect()
            logger.info("connecting to %s", host)

            # store the IRC client to tell it to join and leave channels later
            self.clients[host] = client

            # start a background thread to receive messages, analyze them, and store results
            t = Thread(name="Thread-" + host, target=_monitor_one,
                       kwargs={'source': client, 'diagnosis': self.diagnosis, 'storage': self.storage})
            t.daemon = True
            t.start()

            logger.debug("started monitoring channels on %s in thread %s", host, t.name)

            return self.clients[host]
        except ServerConfigurationError as e:
            logger.warning("Bogus configuration for %s, exception: %s", host, e)
            return None
        except ServerConnectionError as e:
            logger.warning("Failed to connect to %s, exception: %s", host, e)
            return None

    # joins a channel on one of its servers, does nothing on failure
    def join(self, channel):
        # don't join the same channel twice
        if channel in self.channels:
            return

        # get a random server:port hosting this channel
        host = self.find_server(channel)

        # get a client connected to that server:port
        client = self.connect(host)

        # join the channel
        if client:
            client.join(channel)
            logger.debug("will join %s on %s", channel, host)

    # leave a channel
    def leave(self, channel):
        # don't leave a channel we didn't join
        if channel not in self.channels:
            return

        # get the client that joined this channel
        client = self.get_client(channel)

        # tell the client to leave the channel
        if client:
            client.leave(channel)
            logger.debug("will leave channel %s", channel)
        else:
            logger.warning("couldn't find the client connected to %s", channel)

    # find a server hosting a channel
    def find_server(self, channel):
        return random.choice(result['chat_servers'])

    # join big channels, leave offline ones
    def autojoin(self):
        # get a list of channels from Twitch
        # join any channel over n viewers
        # leave any channel under n viewers (including offline ones)
        try:
            data = TwitchApi.stream_list()

            if not data:
                return

            # extract a list of channels from Twitch's API response
            online_channels = ['#' + stream['channel']['name'] for stream in data['streams']]

            # ignore Twitch's data if it looks buggy (no streams online is unlikely)
            if (len(online_channels) == 0):
                return

            # leave any channel out of the top 100 (offline or just further down the list)
            for channel in self.channels:
                if channel not in online_channels:
                    self.leave(channel)

            # join channels over n viewers, leave channels under n viewers
            for stream in data['streams']:
                if stream['viewers'] > self.viewers:
                    self.join('#' + stream['channel']['name'])
                else:
                    self.leave('#' + stream['channel']['name'])
        except KeyError as e:
            logger.warning("got an empty json response to a stream list request %s", e)
            return

    # returns the client connected to the server where a channel was joined
    def get_client(self, channel):
        for client in self.clients.values():
            if channel in client.channels:
                return client
        return None


# read all messages the source generates
def _monitor_one(source, diagnosis, storage):
    for channel, message in source:
        # compute points for the message
        points = diagnosis.points(message)

        # print(message[0:20], channel)

        # store cancer records
        storage.store(channel, points)
