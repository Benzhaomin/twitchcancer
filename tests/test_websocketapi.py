#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.api.websocketapi import publish, create_publishers

# websocketapi.publish()
class TestWebSocketApiPublish(unittest.TestCase):

  def setUp(self):
    self.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

  @patch('twitchcancer.api.websocketapi.PubSubManager.publish', side_effect=KeyboardInterrupt)
  def test_publish(self, publish_topic):
    topic = MagicMock()
    topic.sleep = 1

    try:
      self.loop.run_until_complete(publish(topic))
    except KeyboardInterrupt:
      # we force publish to except out of its infinite loop
      pass

    publish_topic.assert_called_once_with(topic)

# websocketapi.create_publishers()
class TestWebSocketApiCreatePublishers(unittest.TestCase):

  def setUp(self):
    self.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

  def publish_noop(topic):
    return topic

  # TODO: better introspect that stuff
  @patch('twitchcancer.api.websocketapi.publish', side_effect=publish_noop)
  @patch('twitchcancer.api.websocketapi.Storage')
  @patch('twitchcancer.api.websocketapi.PubSubTopic')
  @patch('twitchcancer.api.websocketapi.PubSubVariableTopic')
  @patch('twitchcancer.api.websocketapi.asyncio.gather')
  def test_create_publishers(self, gather, PubSubVariableTopic, PubSubTopic, storage, publish_noop):
    self.loop.run_until_complete(create_publishers())

    # akwardly check that we create PubSubTopics
    self.assertEqual(PubSubTopic.call_count, 3)
    self.assertEqual(PubSubVariableTopic.call_count, 2)

    # check that we created one publish task for each topic
    self.assertEqual(publish_noop.call_count, 5)

    # check that we put the tasks in the loop
    self.assertEqual(len(gather.call_args[0]), 5)

# websocketapi.run()
class TestWebSocketApiRun(unittest.TestCase):
  pass
