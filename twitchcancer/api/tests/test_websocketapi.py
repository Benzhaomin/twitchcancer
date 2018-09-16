import asyncio
import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.api.websocketapi import publish


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


def publish_noop(topic):
    return topic


# websocketapi.create_publishers()
class TestWebSocketApiCreatePublishers(unittest.TestCase):
    pass


# websocketapi.run()
class TestWebSocketApiRun(unittest.TestCase):
    pass
