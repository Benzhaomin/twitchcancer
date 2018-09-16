import time

import irc.client
import logging

logger = logging.getLogger(__name__)


class IRCClientLogger(logging.Logger):

    # ignore log
    def log(self, *args, **kwargs):
        pass

    # ignore info
    def info(self, *args, **kwargs):
        pass

    # ignore debug
    def debug(self, *args, **kwargs):
        pass


# monkey-patch irc.client's logger to avoid n (>5) useless calls to the logger per message
irc.client.log = IRCClientLogger(irc.client.log.name)


class IRCConfigurationError(Exception):
    pass


class IRCConnectionError(Exception):
    pass


class IRCClient(irc.client.SimpleIRCClient):

    def __init__(self, config):
        irc.client.SimpleIRCClient.__init__(self)

        self.connecting = False
        self.autojoin = set()
        self.channels = set()

        try:
            # check the configuration before storing it
            self.config = {
                'server': config['server'],
                'port': config['port'],
                'username': config['username'],
                'password': config['password'],
            }
        except KeyError:
            logger.warning('got an invalid configuration: %s', config)
            raise IRCConfigurationError('config should have the following keys: server, port, username and password')
        except TypeError:
            logger.warning('got a null configuration')
            raise IRCConfigurationError('config should be a dict')

    def _connect(self):
        if not self.connection.is_connected() and not self.connecting:
            try:
                self.connect(self.config['server'], self.config['port'], self.config['username'],
                             self.config['password'])
                self.connecting = True
            except irc.client.ServerConnectionError as x:
                # stay open to further retries
                self.connecting = False
                logger.warning('connecting to %s failed with %s', self, x)
                raise IRCConnectionError('Connection to {0} failed'.format(self))

    def __str__(self):
        return self.config['server'] + ':' + str(self.config['port'])

    def join(self, channel):
        # connect if necessary (and auto-join on welcome)
        if not self.connection.is_connected():
            logger.debug('%s not connected, will join %s later', self, channel)
            self.autojoin.add(channel)
            return

        # make sure the channel exists
        if not irc.client.is_channel(channel):
            logger.warning('channel %s not found on %s', channel, self)
            return

        # don't join the same channel twice
        if channel in self.channels:
            return

        # send an IRC JOIN command
        self.connection.join(channel)
        logger.info("joining %s", channel)

        # save the new channel
        self.channels.add(channel)

    def leave(self, channel):
        # don't even think about unknown channels
        if channel not in self.channels:
            return

        # just don't do anything if we're not connected
        if not self.connection.is_connected():
            logger.debug('%s not connected, no need to leave %s', self, channel)
            return

        # make sure the channel exists
        if not irc.client.is_channel(channel):
            logger.warning('channel %s not found on %s', channel, self)
            self.channels.remove(channel)
            return

        # send an IRC PART command
        self.connection.part(channel)
        logger.info("leaving %s", channel)

        # forget about that channel
        self.channels.remove(channel)

    def on_welcome(self, connection, event):
        logger.debug('welcome, joining %s', self.autojoin)

        self.connecting = False

        for channel in set(self.autojoin):
            self.autojoin.remove(channel)
            self.join(channel)

    def on_join(self, connection, event):
        logger.debug('joined %s', event.target)

    def on_pubmsg(self, connection, event):
        # forward the message to a callback if any
        def do_nothing(channel, msg):
            return None

        method = getattr(self, "call_on_pubmsg", do_nothing)
        method(event.target, event.arguments[0])

    def on_disconnect(self, connection, event):
        # schedule all channels to be re-joined
        self.autojoin = self.channels

        # clear active channels until then
        self.channels.clear()

        # try to reconnect
        try:
            self._connect()
        except IRCConnectionError:
            # try a second and last time to reconnect
            try:
                logger.warning('first attempt to reconnect after disconnect failed on %s, trying again in a minute',
                               self)

                # wait for a bit, it's ok because we're not on the main thread
                time.sleep(60)

                self._connect()
            except IRCConnectionError:
                # won't reconnect unless told to
                # TODO: we should let the thread die and bubble the error up
                #       currently, we will simply report no connected channels but still accept join() and leave() calls
                #       our user might be thinking we actually are recording
                logger.warning('second attempt to reconnect after disconnect failed on %s, no further retries', self)


def debug_on_msg(msg):
    print(msg)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

    config = {
        'server': 'irc.ca.us.mibbit.net',
        'port': 6667,
        'username': 'testpython',
        'password': None,
    }
    c = IRCClient(config)
    c.call_on_pubmsg = debug_on_msg
    c.join('#testkappa')
    c.join('#testkappa2')
    c._connect()
    c.start()
