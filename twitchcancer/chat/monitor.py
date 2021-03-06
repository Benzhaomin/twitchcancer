import logging

logger = logging.getLogger(__name__)


class Monitor:

    def __init__(self, viewers=1000):
        self.viewers = viewers

    # join and leave channels, forever
    def run(self):
        pass

    # connect to a server
    def connect(self, server):
        # don't connect to the same server twice
        pass

    # join a channel
    def join(self, channel):
        # don't join the same channel twice
        # use self.find_server()
        pass

    # leave a channel
    def leave(self, channel):
        pass

    # find a server hosting a channel
    def find_server(self, channel):
        return None

    # join big channels, leave offline ones
    def autojoin(self):
        # get a list of channels from https://api.twitch.tv/kraken/streams/?limit=100
        # join any channel over n viewers
        # leave any channel under n viewers (including offline ones)
        pass
