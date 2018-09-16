import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.api.pubsubmanager import PubSubManager


# PubSubManager.instance()
class TestPubSubManagerInstance(unittest.TestCase):

    # check that we only store one instance of any topic
    @patch('twitchcancer.api.pubsubmanager.PubSubManager.__new__', side_effect=PubSubManager.__new__)
    def test_all(self, new):
        PubSubManager.instance()
        PubSubManager.instance()

        self.assertEqual(new.call_count, 1)


# PubSubManager.subscribe()
class TestPubSubManagerSubscribe(unittest.TestCase):

    # subscribe to a new topic
    def test_subscribe_new(self):
        p = PubSubManager()
        p.subscribe("client", "topic")

        # check that the topic was created
        self.assertEqual(len(p.subscriptions.keys()), 1)

        # check that we are subbed
        self.assertTrue("client" in p.subscriptions["topic"])
        self.assertTrue(len(p.subscriptions["topic"]), 1)

    # subscribe to an existing topic
    def test_subscribe_existing(self):
        p = PubSubManager()
        p.subscriptions["topic"] = {"other client"}

        p.subscribe("client", "topic")

        # check that the topic was reused
        self.assertEqual(len(p.subscriptions.keys()), 1)

        # check that we are subbed
        self.assertTrue("client" in p.subscriptions["topic"])
        self.assertTrue(len(p.subscriptions["topic"]), 2)


# PubSubManager.unsubscribe()
class TestPubSubManagerUnsubscribe(unittest.TestCase):

    # unsubscribe from an existing topic
    def test_unsubscribe_existing(self):
        p = PubSubManager()
        p.subscriptions["topic"] = {"client", "other client"}

        p.unsubscribe("client", "topic")

        # check that we are not subbed anymore
        self.assertTrue("client" not in p.subscriptions["topic"])

    # unsubscribe from an existing topic as the last client
    def test_unsubscribe_existing_last(self):
        p = PubSubManager()
        p.subscriptions["topic"] = {"client"}

        p.unsubscribe("client", "topic")

        # check that the topic was garbage collected
        self.assertTrue("topic" not in p.subscriptions)

    # unsubscribe from an unknown topic
    def test_unsubscribe_not_existing(self):
        p = PubSubManager()

        p.unsubscribe("client", "topic")

        # check that the topic wasn't created
        self.assertTrue("topic" not in p.subscriptions)


# PubSubManager.unsubscribe_all()
class TestPubSubManagerUnsubscribeAll(unittest.TestCase):

    # check that unsubcribe is called for all topics
    @patch('twitchcancer.api.pubsubmanager.PubSubManager.unsubscribe')
    def test_unsubscribe_all(self, unsubscribe):
        p = PubSubManager()
        p.subscriptions["topic"] = {"client"}
        p.subscriptions["topic 2"] = {"client"}

        p.unsubscribe_all("client")

        # check the number of calls
        # TODO: check the actual arguments of each call
        self.assertEqual(unsubscribe.call_count, 2)


# PubSubManager.publish()
class TestPubSubManagerPublish(unittest.TestCase):

    # check that a client subscribed to a topic gets data on publish()
    def test_publish_subscribed(self):
        # subscribe a client to a topic
        client = MagicMock()
        p = PubSubManager()
        p.subscriptions["topic"] = {client}

        # publish data for that topic
        topic = MagicMock()
        topic.payload = MagicMock(return_value="payload")
        p.publish(topic)

        # make sure the client got data
        client.send.assert_called_once_with("topic", "payload")

    # check that a client not subscribed to a topic doesn't get data on publish()
    def test_publish_not_subscribed(self):
        # subscribe a client to a topic
        client = MagicMock()
        p = PubSubManager()
        p.subscriptions["topic"] = {client}

        # publish data for another topic
        topic = MagicMock()
        topic.match = MagicMock(return_value=False)
        p.publish(topic)

        # make sure the client didn't get called
        self.assertFalse(client.send.called)


# PubSubManager.publish_one()
class TestPubSubManagerPublishOne(unittest.TestCase):

    def test_publish_one_existing(self):
        client = MagicMock()

        topic = MagicMock()
        topic.payload = MagicMock(return_value="payload")

        with patch('twitchcancer.api.pubsubtopic.PubSubTopic.find', return_value=topic):
            PubSubManager().publish_one(client, "topic")

            # make sure the client got data
            client.send.assert_called_once_with("topic", "payload")

    @patch('twitchcancer.api.pubsubtopic.PubSubTopic.find', return_value=None)
    def test_publish_one_not_existing(self, find):
        client = MagicMock()

        PubSubManager().publish_one(client, "topic")

        # make sure the client didn't get called
        self.assertFalse(client.send.called)
