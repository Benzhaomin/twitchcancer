#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.api.pubsubmanager import PubSubManager

# PubSubManager.instance()
class TestPubSubManagerInstance(unittest.TestCase):

  # quickly test most cases
  def test_all(self):
    with patch('twitchcancer.api.pubsubmanager.PubSubManager.__new__', side_effect=PubSubManager.__new__) as m:
      PubSubManager.instance()
      PubSubManager.instance()
      m.assert_called_once()

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
    p.subscriptions["topic"] = set(["other client"])

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
    p.subscriptions["topic"] = set(["client", "other client"])

    p.unsubscribe("client", "topic")

    # check that we are not subbed anymore
    self.assertTrue("client" not in p.subscriptions["topic"])

  # unsubscribe from an existing topic as the last client
  def test_unsubscribe_existing_last(self):
    p = PubSubManager()
    p.subscriptions["topic"] = set(["client"])

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
  def test_unsubscribe_all(self):
    with patch('twitchcancer.api.pubsubmanager.PubSubManager.unsubscribe') as m:
      p = PubSubManager()
      p.subscriptions["topic"] = set(["client"])
      p.subscriptions["topic 2"] = set(["client"])

      p.unsubscribe_all("client")

      # check the number of calls
      # TODO: check the actual arguments of each call
      self.assertEqual(len(m.mock_calls), 2)

# PubSubManager.publish()
class TestPubSubManagerPublish(unittest.TestCase):

  # check that a client subscribed to a topic gets data on publish()
  def test_publish_subscribed(self):
    # subscribe a client to a topic
    client = MagicMock()
    p = PubSubManager()
    p.subscriptions["topic"] = set([client])

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
    p.subscriptions["topic"] = set([client])

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

    with patch('twitchcancer.api.pubsubtopic.PubSubTopic.find', return_value=topic) as m:
      PubSubManager().publish_one(client, "topic")

      # make sure the client got data
      client.send.assert_called_once_with("topic", "payload")

  def test_publish_one_not_existing(self):
    client = MagicMock()
    topic = MagicMock()

    with patch('twitchcancer.api.pubsubtopic.PubSubTopic.find', return_value=None) as m:
      PubSubManager().publish_one(client, "topic")

      # make sure the client didn't get called
      self.assertFalse(client.send.called)
