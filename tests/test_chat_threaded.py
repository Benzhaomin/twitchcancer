#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import unittest
from unittest.mock import patch, Mock, MagicMock

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

  # check that connecting to a new server works correctly
  @patch('twitchcancer.chat.irc.threaded.IRC')
  @patch('twitchcancer.chat.irc.threaded.Thread')
  def test_default(self, thread, irc):
    ip = "127.0.0.1"
    port = "80"
    server = ip+":"+port

    t = ThreadedIRCMonitor(1000)
    t.connect(server)

    # we should have created an IRC client for that server
    irc.assert_called_once_with(ip, port)

    # we should have stored the new client in our clients list
    self.assertEqual(len(t.clients.keys()), 1)

  # check that connecting twice to the same server does nothing
  @patch('twitchcancer.chat.irc.threaded.IRC')
  def test_twice_same(self, irc):
    ip = "127.0.0.1"
    port = "80"
    server = ip+":"+port

    t = ThreadedIRCMonitor(1000)
    t.clients = { server: {} }

    t.connect(server)

    # we should not even try to connect to that server
    self.assertFalse(irc.called)

    # we should have stored the first client only
    self.assertEqual(len(t.clients.keys()), 1)

# ThreadedIRCMonitor.join
class TestChatThreadedJoin(unittest.TestCase):

  # check that find_server failures are handled
  @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.find_server', return_value=None)
  @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.connect')
  def test_no_server(self, connect, find_server):
    t = ThreadedIRCMonitor(1000)
    channel = 'channel'

    t.join(channel)

    # we shouldn't do anything for channels without server
    self.assertTrue(find_server.called)
    self.assertFalse(connect.called)

  # check that joining a new channel works correctly
  @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.find_server', return_value="client")
  @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.connect')
  def test_default(self, connect, find_server):
    t = ThreadedIRCMonitor(1000)
    channel = 'channel'
    client = MagicMock()
    client.channels = []
    t.clients = { 'client': client }

    t.join(channel)

    # we should have searched for a suitable server
    find_server.assert_called_once_with(channel)

    # we should connect to that server
    connect.assert_called_once_with("client")

    # we should have transmitted the join call to the IRC client
    client.join.assert_called_once_with(channel)

  # check that joining the same channel twice does nothing
  @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.find_server', return_value="client")
  @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.connect')
  def test_twice(self, connect, find_server):
    t = ThreadedIRCMonitor(1000)
    channel = 'channel'
    client = MagicMock()
    client.channels = [channel]
    t.clients = { 'client': client }

    t.join(channel)

    # we shouldn't do anything on duplicate channels
    self.assertFalse(find_server.called)
    self.assertFalse(connect.called)
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
    t.clients = { 'client': client }

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
    t.clients = { 'client': client }

    with patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.get_client', return_value=client) as get_client:
      t.leave(channel)

      # we should search for the client connected to that channel
      get_client.assert_called_once_with(channel)

      # we should transmit the leave call to that client
      client.leave.assert_called_once_with(channel)

# ThreadedIRCMonitor.find_server
class TestChatThreadedFindServer(unittest.TestCase):

  def setUp(self):
    self.monitor = ThreadedIRCMonitor(1000)

  # check that a None response is handled correctly
  @patch('twitchcancer.utils.twitchapi.TwitchApi.chat_properties', return_value=None)
  def test_no_response(self, chat_properties):
    server = self.monitor.find_server("")

    self.assertIsNone(server)

  # check that an empty response is handled correctly
  @patch('twitchcancer.utils.twitchapi.TwitchApi.chat_properties', return_value={})
  def test_empty_json_response(self, chat_properties):
    server = self.monitor.find_server("")

    self.assertIsNone(server)

  # check that we get a server from Twitch when the request worked
  @patch('twitchcancer.utils.twitchapi.TwitchApi.chat_properties', return_value={"chat_servers": ["foo"]})
  def test_default(self, chat_properties):
    server = self.monitor.find_server("")

    self.assertEqual(server, "foo")

  # check that server selection is random
  @patch('twitchcancer.utils.twitchapi.TwitchApi.chat_properties', return_value={"chat_servers": ["1", "2", "3", "4", "5"]})
  def test_random(self, chat_properties):
    # ask for 10 servers
    servers = [self.monitor.find_server("") for n in range(10)]

    # we should have gotten more than 1 unique server
    self.assertGreater(len(set(servers)), 1)

# ThreadedIRCMonitor.autojoin
class TestChatThreadedAutojoin(unittest.TestCase):

  def build_streams(streams):
    return {'streams': [{
      "viewers": viewers,
      "channel": { "name": channel }
    } for channel, viewers in streams.items()]}

  def setUp(self):
    self.monitor = ThreadedIRCMonitor(1000)

  # check that a None response is handled correctly
  @patch('twitchcancer.utils.twitchapi.TwitchApi.stream_list', return_value=None)
  def test_no_response(self, stream_list):
    self.monitor.autojoin()

  # check that an empty response is handled correctly
  @patch('twitchcancer.utils.twitchapi.TwitchApi.stream_list', return_value={})
  def test_empty_json_response(self, stream_list):
    self.monitor.autojoin()

  # check that an empty stream list is ignored
  @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.leave')
  @patch('twitchcancer.utils.twitchapi.TwitchApi.stream_list', return_value=build_streams({}))
  def test_empty_json_response(self, stream_list, leave):
    client = MagicMock()
    client.channels = ["#foo"]
    self.monitor.clients = { 'client': client }

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
    self.monitor.clients = { 'client': client }

    self.monitor.autojoin()

    leave.assert_called_once_with("#foo")

  # check that we leave channels that went offline
  @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.join')
  @patch('twitchcancer.chat.irc.threaded.ThreadedIRCMonitor.leave')
  @patch('twitchcancer.utils.twitchapi.TwitchApi.stream_list', return_value=build_streams({'bar': 2000}))
  def test_leave_offline_channels(self, stream_list, leave, join):
    client = MagicMock()
    client.channels = ["#foo"]
    self.monitor.clients = { 'client': client }

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
    channel = 'channel'
    client = MagicMock()
    client.channels = ["#foo"]
    self.monitor.clients = { 'client': client }

    result = self.monitor.get_client("#foo")

    self.assertEqual(result, client)
