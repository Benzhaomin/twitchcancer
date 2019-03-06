import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.chat.irc.irc import ServerConfigurationError, ServerConnectionError
from twitchcancer.chat.irc.threaded import ThreadedIRCMonitor


# ThreadedIRCMonitor.__init__
class TestChatThreadedInit(unittest.TestCase):
    pass


# ThreadedIRCMonitor.__getattr__
class TestChatThreadedGetAttr(unittest.TestCase):

    # check that we can access the channels attribute
    def test_default(self):
        t = ThreadedIRCMonitor(1000)

        self.assertEqual(t.channels, [])

    # check that the channels attribute is correctly filled with client channels
    def test_channels(self):
        t = ThreadedIRCMonitor(1000)
        client1 = MagicMock()
        client1.channels = ['foo', 'bar']
        client2 = MagicMock()
        client2.channels = ['baz']

        t.clients = {
            'client1': client1,
            'client2': client2
        }

        self.assertEqual(sorted(t.channels), sorted(['foo', 'bar', 'baz']))


# ThreadedIRCMonitor.run
class TestChatThreadedRun(unittest.TestCase):

    # check that the mainloop autojoins and sleeps
    @patch('time.sleep', side_effect=KeyboardInterrupt)
    @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.autojoin')
    def test_default(self, autojoin, sleep):
        t = ThreadedIRCMonitor(1000)
        t.run()

        self.assertEqual(autojoin.call_count, 1)
        self.assertEqual(sleep.call_count, 1)


# ThreadedIRCMonitor.connect
class TestChatThreadedConnect(unittest.TestCase):

    def setUp(self):
        self.monitor = ThreadedIRCMonitor(1000)
        self.ip = "127.0.0.1"
        self.port = "80"
        self.host = self.ip + ":" + self.port

    # check that connecting to a new server works correctly
    @patch('twitchcancer.chat.irc.threaded.IRC.__init__', return_value=None)
    @patch('twitchcancer.chat.irc.threaded.IRC.connect')
    @patch('twitchcancer.chat.irc.threaded.Thread.start')
    def test_default(self, start_thread, connect_irc, init_irc):
        result = self.monitor.connect(self.host)

        # we should have created an IRC client for that server and connected to it
        init_irc.assert_called_once_with(self.ip, self.port)
        connect_irc.assert_called_once_with()

        # we should have started a background thread for that server
        start_thread.assert_called_once_with()

        # we should have stored the new client in our clients list
        self.assertEqual(len(self.monitor.clients.keys()), 1)

        # we should get the new server
        self.assertIsNotNone(result)

    # check that connecting twice to the same server does nothing
    @patch('twitchcancer.chat.irc.threaded.IRC')
    @patch('twitchcancer.chat.irc.threaded.Thread')
    def test_twice_same(self, thread, irc):
        client = MagicMock()
        self.monitor.clients = {self.host: client}

        result = self.monitor.connect(self.host)

        # we should not create an IRC client
        self.assertFalse(irc.called)

        # we should not create a background thread
        self.assertFalse(thread.called)

        # we should have stored the first client only
        self.assertEqual(len(self.monitor.clients.keys()), 1)

        # we should get the old server
        self.assertEqual(result, client)

    # check that configuration error are handled
    @patch('twitchcancer.chat.irc.threaded.IRC.__init__', return_value=None, side_effect=ServerConfigurationError)
    def test_configuration_error(self, irc):
        result = self.monitor.connect(self.host)

        self.assertIsNone(result)

    # check that configuration error are handled
    @patch('twitchcancer.chat.irc.threaded.IRC.connect', side_effect=ServerConnectionError)
    def test_connection_error(self, irc):
        result = self.monitor.connect(self.host)

        self.assertIsNone(result)


# ThreadedIRCMonitor.join
class TestChatThreadedJoin(unittest.TestCase):

    def setUp(self):
        self.monitor = ThreadedIRCMonitor(1000)
        self.channel = 'channel'

    # check that we ignore channels without host
    @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.find_server', return_value=None)
    @patch('twitchcancer.chat.irc.irc.IRC.join')
    def test_no_server(self, ircjoin, find_server):
        self.monitor.join(self.channel)

        # we shouldn't have exploded
        self.assertNotIn(self.channel, self.monitor.channels)

    # check that joining a new channel works correctly
    @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.find_server', return_value="host")
    def test_default(self, find_server):
        client = MagicMock()

        with patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.connect', return_value=client) as connect:
            self.monitor.join(self.channel)

            # we should connect to that server
            connect.assert_called_once_with("host")

            # we should have transmitted the join call to the IRC client
            client.join.assert_called_once_with(self.channel)

    # check that joining the same channel twice does nothing
    @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.find_server', return_value="client")
    @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.connect')
    def test_twice(self, connect, find_server):
        client = MagicMock()
        client.channels = [self.channel]
        clients = {'client': client}
        self.monitor.clients = clients

        self.monitor.join(self.channel)

        # we shouldn't do anything on duplicate channels
        self.assertEqual(self.monitor.clients, clients)
        self.assertFalse(client.join.called)


# ThreadedIRCMonitor.leave
class TestChatThreadedLeave(unittest.TestCase):

    # check that we ignore channels we didn't join
    @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.get_client')
    def test_not_joined(self, get_client):
        t = ThreadedIRCMonitor(1000)
        t.leave("foo")

        self.assertFalse(get_client.called)

    # check that we handle get_client failures
    def test_no_client(self):
        t = ThreadedIRCMonitor(1000)
        channel = 'channel'
        client = MagicMock()
        client.channels = [channel]
        t.clients = {'client': client}

        with patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.get_client', return_value=None) as get_client:
            t.leave(channel)

            # we should search for the client connected to that channel
            get_client.assert_called_once_with(channel)

            # we shouldn't talk to the IRC client
            self.assertFalse(client.leave.called)

    # check that we leave channels we joined
    def test_default(self):
        t = ThreadedIRCMonitor(1000)
        channel = 'channel'
        client = MagicMock()
        client.channels = [channel]
        t.clients = {'client': client}

        with patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.get_client', return_value=client) as get_client:
            t.leave(channel)

            # we should search for the client connected to that channel
            get_client.assert_called_once_with(channel)

            # we should transmit the leave call to that client
            client.leave.assert_called_once_with(channel)


def build_streams(streams):
    return {'streams': [{
        "viewers": viewers,
        "channel": {"name": channel}
    } for channel, viewers in streams.items()]}


# ThreadedIRCMonitor.autojoin
class TestChatThreadedAutojoin(unittest.TestCase):

    def setUp(self):
        self.monitor = ThreadedIRCMonitor(1000)

    # check that a None response is handled correctly
    @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.leave')
    @patch('twitchcancer.utils.twitchapi.TwitchApi.stream_list', return_value=None)
    def test_no_response(self, stream_list, leave):
        self.monitor.autojoin()

        self.assertFalse(leave.called)

    # check that an empty response is handled correctly
    @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.leave')
    @patch('twitchcancer.utils.twitchapi.TwitchApi.stream_list', return_value={})
    def test_empty_json_response(self, stream_list, leave):
        self.monitor.autojoin()

        self.assertFalse(leave.called)

    # check that an empty stream list is ignored
    @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.leave')
    @patch('twitchcancer.utils.twitchapi.TwitchApi.stream_list', return_value=build_streams({}))
    def test_empty_json_response2(self, stream_list, leave):
        client = MagicMock()
        client.channels = ["#foo"]
        self.monitor.clients = {'client': client}

        self.monitor.autojoin()

        self.assertFalse(leave.called)

    # check that we join channels over n viewers
    @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.join')
    @patch('twitchcancer.utils.twitchapi.TwitchApi.stream_list', return_value=build_streams({'foo': 2000, 'bar': 100}))
    def test_join_channels(self, stream_list, join):
        self.monitor.autojoin()

        join.assert_called_once_with("#foo")

    # check that we leave channels that went below n viewers
    @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.leave')
    @patch('twitchcancer.utils.twitchapi.TwitchApi.stream_list', return_value=build_streams({'foo': 100}))
    def test_leave_channel_below_n_viewers(self, stream_list, leave):
        client = MagicMock()
        client.channels = ["#foo"]
        self.monitor.clients = {'client': client}

        self.monitor.autojoin()

        leave.assert_called_once_with("#foo")

    # check that we leave channels that went offline
    @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.join')
    @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.leave')
    @patch('twitchcancer.utils.twitchapi.TwitchApi.stream_list', return_value=build_streams({'bar': 2000}))
    def test_leave_offline_channels(self, stream_list, leave, join):
        client = MagicMock()
        client.channels = ["#foo"]
        self.monitor.clients = {'client': client}

        self.monitor.autojoin()

        leave.assert_called_once_with("#foo")


# ThreadedIRCMonitor.get_client
class TestChatThreadedGetClient(unittest.TestCase):

    def setUp(self):
        self.monitor = ThreadedIRCMonitor(1000)

    # check that we get None for unknown channels
    def test_unknown_channel(self):
        result = self.monitor.get_client("#foo")

        self.assertIsNone(result)

    # check that we get the right client
    def test_known_channel(self):
        client = MagicMock()
        client.channels = ["#foo"]
        self.monitor.clients = {'client': client}

        result = self.monitor.get_client("#foo")

        self.assertEqual(result, client)
