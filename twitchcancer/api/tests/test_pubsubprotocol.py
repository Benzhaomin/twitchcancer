import datetime
import json
import unittest
from unittest.mock import patch

from twitchcancer.api.pubsubprotocol import PubSubProtocol

PubSubProtocol.peer = "test"


# PubSubProtocol.__str__()
class TestPubSubProtocolStr(unittest.TestCase):

    def test_str(self):
        p = PubSubProtocol()
        p.peer = "foo"
        self.assertEqual(str(p), "foo")


# PubSubProtocol.onConnect()
class TestPubSubProtocolOnConnect(unittest.TestCase):

    # check that we don't fail (we shouldn't do anything either)
    def test_no_op(self):
        p = PubSubProtocol()
        p.onConnect(None)


# PubSubProtocol.onOpen()
class TestPubSubProtocolOnOpen(unittest.TestCase):

    # check that we don't fail (we shouldn't do anything either)
    def test_no_op(self):
        p = PubSubProtocol()
        p.onOpen()


# PubSubProtocol.onClose()
class TestPubSubProtocolOnClose(unittest.TestCase):

    # check that we unsubscribe clients when they disconnect
    @patch('twitchcancer.api.pubsubmanager.PubSubManager.unsubscribe_all')
    def test_unsubscribe_all(self, unsubscribe_all):
        p = PubSubProtocol()
        p.onClose(True, 0, None)
        unsubscribe_all.assert_called_once_with(p)


# PubSubProtocol.onMessage()
class TestPubSubProtocolOnMessage(unittest.TestCase):

    # check that we handle bogus payloads (by doing nothing)
    @patch('twitchcancer.api.pubsubmanager.PubSubManager.instance')
    def test_bogus_payload(self, instance):
        p = PubSubProtocol()
        p.onMessage(b'', True)
        p.onMessage(b'foo', True)
        p.onMessage(b'{foo}', True)
        p.onMessage(b'{"foo"}', True)

        self.assertFalse(instance.called)

    # check that we handle unknown commands (by doing nothing)
    @patch('twitchcancer.api.pubsubmanager.PubSubManager.instance')
    def test_unknown_command(self, instance):
        p = PubSubProtocol()
        p.onMessage(b'{"foo":"bar"}', True)

        self.assertFalse(instance.called)

    # check that we subscribe clients
    @patch('twitchcancer.api.pubsubmanager.PubSubManager.subscribe')
    def test_subscribe_command(self, subscribe):
        p = PubSubProtocol()
        p.onMessage(b'{"subscribe":"topic"}', True)

        subscribe.assert_called_once_with(p, "topic")

    # check that we publish data once on subscribing clients
    @patch('twitchcancer.api.pubsubmanager.PubSubManager.publish_one')
    def test_subscribe_publish_one(self, publish_one):
        p = PubSubProtocol()
        p.onMessage(b'{"subscribe":"topic"}', True)

        publish_one.assert_called_once_with(p, "topic")

    # check that we unsubscribe clients
    @patch('twitchcancer.api.pubsubmanager.PubSubManager.unsubscribe')
    def test_unsubscribe_command(self, unsubscribe):
        p = PubSubProtocol()
        p.onMessage(b'{"unsubscribe":"topic"}', True)

        unsubscribe.assert_called_once_with(p, "topic")

    # check that we response to requests
    @patch('twitchcancer.api.requesthandler.RequestHandler.handle', return_value="response")
    @patch('twitchcancer.api.pubsubprotocol.PubSubProtocol.send')
    def test_request_command(self, send, handle):
        p = PubSubProtocol()
        p.onMessage(b'{"request":"topic"}', True)

        handle.assert_called_once_with({"request": "topic"})
        send.assert_called_once_with("topic", "response")


# PubSubProtocol.send()
class TestPubSubProtocolSend(unittest.TestCase):

    # check that we handle bogus payloads (by doing nothing)
    @patch('twitchcancer.api.pubsubprotocol.PubSubProtocol.sendMessage')
    def test_bogus_payload(self, send_message):
        p = PubSubProtocol()
        p.send("topic", p)
        p.send(p, {'data': 'bar'})
        p.send(p, p)

        self.assertFalse(send_message.called)

    # check that we send the message to the client
    @patch('twitchcancer.api.pubsubprotocol.PubSubProtocol.sendMessage')
    def test_send_message(self, send_message):
        p = PubSubProtocol()
        p.send("foo", "bar")
        self.assertEqual(send_message.call_count, 1)

    # check that we send the message to the client
    @patch('twitchcancer.api.pubsubprotocol.PubSubProtocol.sendMessage')
    def test_jsonify(self, send_message):
        now = datetime.datetime.now()

        p = PubSubProtocol()
        p.send("foo", now)

        args, kwargs = send_message.call_args
        actual = json.loads(args[0].decode('utf8'))

        expected = {"topic": "foo", "data": now.isoformat()}

        self.assertEqual(actual, expected)
