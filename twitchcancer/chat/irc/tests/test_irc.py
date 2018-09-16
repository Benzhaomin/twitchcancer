import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.chat.irc.irc import IRC, ServerConfigurationError, ServerConnectionError
from twitchcancer.chat.irc.ircclient import IRCConfigurationError, IRCConnectionError


# build a client with default config
class IRCTestCase(unittest.TestCase):

    def setUp(self):
        self.client = IRC(MagicMock(), MagicMock())


# IRC.__init__
class TestIRCInit(unittest.TestCase):

    # check that we handle exceptions from the IRCClient
    @patch('twitchcancer.chat.irc.irc.IRCClient', side_effect=IRCConfigurationError)
    def test_configuration_exception(self, ircclient):
        self.assertRaises(ServerConfigurationError, lambda: IRC("foo", "80"))

    # check that we initialize members correctly
    @patch('twitchcancer.chat.irc.irc.IRCClient')
    def test_default(self, ircclient):
        client = IRC("foo", "80")

        self.assertIsNotNone(client.messages)
        self.assertIsNotNone(client.client)
        self.assertEqual(client.host, "foo")
        self.assertEqual(client.port, 80)
        self.assertIsNone(client.client_thread)


# IRC.connect
class TestIRCConnect(IRCTestCase):

    # check that we handle exceptions from the IRCClient
    @patch('twitchcancer.chat.irc.irc.IRCClient._connect', side_effect=IRCConnectionError)
    def test_configuration_exception(self, ircclient):
        # we should raise another exception
        self.assertRaises(ServerConnectionError, lambda: self.client.connect())

        # we should not have started a thread
        self.assertIsNone(self.client.client_thread)

    # check that we connect and start a thread to receive messages
    @patch('twitchcancer.chat.irc.ircclient.IRCClient._connect')
    @patch('twitchcancer.chat.irc.threaded.Thread.start')
    def test_default(self, start_thread, ircconnect):
        self.client.connect()

        # we should connect to the IRC server
        ircconnect.assert_called_once_with()

        # we should have started a background thread for that server
        start_thread.assert_called_once_with()
        self.assertIsNotNone(self.client.client_thread)


# IRC.__iter__
class TestIRCIter(IRCTestCase):

    def setUp(self):
        super().setUp()

        self.client.client.join = MagicMock()
        self.channel = "#foo"

    # check that we transmit the call to our client
    def test_default(self):
        self.client.join(self.channel)

        self.client.client.join.assert_called_once_with(self.channel)


# IRC.__next__
class TestIRCNext(IRCTestCase):

    def setUp(self):
        super().setUp()

        self.client.messages = MagicMock()
        self.client.messages.get = MagicMock(side_effect=["1", "2", "3"])

    # check that the several call to next() return messages in order
    def test_default(self):
        self.assertEqual(self.client.__next__(), "1")
        self.assertEqual(self.client.__next__(), "2")
        self.assertEqual(self.client.__next__(), "3")


# IRC.join
class TestIRCJoin(IRCTestCase):

    def setUp(self):
        super().setUp()

        self.client.client.join = MagicMock()
        self.channel = "#foo"

    # check that we transmit the call to our client
    def test_default(self):
        self.client.join(self.channel)

        self.client.client.join.assert_called_once_with(self.channel)


# IRC.leave
class TestIRCLeave(IRCTestCase):

    def setUp(self):
        super().setUp()

        self.client.client.leave = MagicMock()
        self.channel = "#foo"

    # check that we transmit the call to our client
    def test_default(self):
        self.client.leave(self.channel)

        self.client.client.leave.assert_called_once_with(self.channel)


# IRC.__getattr__
class TestIRCGetAttr(IRCTestCase):

    def setUp(self):
        super().setUp()

        self.channels = ["#foo"]
        self.client.client.channels = self.channels

    # check that we transmit the call to our client
    def test_default(self):
        self.assertEqual(self.client.channels, self.channels)


# IRC._client_thread
class TestIRCClientThread(IRCTestCase):

    def setUp(self):
        super().setUp()

        self.client.client = MagicMock()

    # check that we set the onPubMsg callback and start the client thread
    def test_default(self):
        self.client._client_thread(self.client.client)

        self.assertEqual(self.client.client.call_on_pubmsg, self.client._on_pubmsg)
        self.client.client.start.assert_called_once_with()


# IRC._on_pubmsg
class TestIRCOnPubMsg(IRCTestCase):

    # check that messages are put on the messages queue
    def test_default(self):
        self.client.messages = MagicMock()
        channel = "channel"
        msg = "msg"

        self.client._on_pubmsg(channel, msg)

        self.client.messages.put.assert_called_once_with((channel, msg))

    # check that messages are striped before being put on the message queue
    def test_messages_strip(self):
        self.client.messages = MagicMock()
        channel = "channel"
        msg = " msg "

        self.client._on_pubmsg(channel, msg)

        self.client.messages.put.assert_called_once_with((channel, msg.strip()))

    # check that empty messages are ignored
    def test_empty_messages(self):
        self.client.messages = MagicMock()
        channel = "channel"
        msg = ""

        self.client._on_pubmsg(channel, msg)

        self.assertFalse(self.client.messages.put.called)
