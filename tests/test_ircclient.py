#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import unittest
from unittest.mock import patch, Mock, MagicMock

import irc.client

from twitchcancer.chat.irc.ircclient import IRCClient

# IRCClient.__init__
class TestIRCClientInit(unittest.TestCase):

  # check that we raise an exception when the config is bogus
  def test_bogus_config(self):
    self.assertRaises(TypeError, lambda: IRCClient(None))
    self.assertRaises(TypeError, lambda: IRCClient({}))
    self.assertRaises(TypeError, lambda: IRCClient({'server': ''}))
    self.assertRaises(TypeError, lambda: IRCClient({'port': ''}))
    self.assertRaises(TypeError, lambda: IRCClient({'username': ''}))
    self.assertRaises(TypeError, lambda: IRCClient({'password': ''}))

  # check that we properly merge a valid config
  def test_config(self):
    config = {
      'server': 'foo',
      'port': 80,
      'username': 'bar',
      'password': 'baz',
    }

    client = IRCClient(config)

    self.assertEqual(config, client.config)

# IRCClient._connect
class TestIRCClientConnect(unittest.TestCase):

  def setUp(self):
    self.channel = "#foo"

    self.client = IRCClient(MagicMock())
    self.client.connection = MagicMock()
    self.client.connect = MagicMock()

  # check that we ignore connect calls when already connected
  def test_connected(self):
    self.client._connect()

    self.assertFalse(self.client.connect.called)

  # check that we ignore connect calls when already connecting
  def test_connecting(self):
    self.client.connection.is_connected = Mock(return_value=False)
    self.client.connecting = True

    self.client._connect()

    self.assertFalse(self.client.connect.called)

  # check that we handle connect failures
  def test_exception(self):
    self.client.config = MagicMock()
    self.client.__str__ = Mock(return_value="foo:bar")
    self.client.connection.is_connected = Mock(return_value=False)
    self.client.connect = MagicMock(side_effect=irc.client.ServerConnectionError)

    self.client._connect()

    self.assertTrue(self.client.connect.called)
    self.assertFalse(self.client.connecting)

# IRCClient.__str__
class TestIRCClientStr(unittest.TestCase):

  # check that our config is formatted properly to represent self as a string
  def test_default(self):
    client = IRCClient({'server': 'foo', 'port': 80, 'username': '', 'password': ''})

    self.assertEqual(str(client), "foo:80")

# IRCClient.join
class TestIRCClientJoin(unittest.TestCase):

  def setUp(self):
    self.channel = "#foo"

    self.client = IRCClient(MagicMock())
    self.client.connection = MagicMock()
    self.client._connect = MagicMock()

  # check that we auto-connect and schedule a join when not connected
  def test_not_connected(self):
    self.client.connection.is_connected = Mock(return_value=False)

    self.client.join(self.channel)

    self.assertIn(self.channel, self.client.autojoin)
    self.assertTrue(self.client._connect.called)

  # check that we ignore requests for joining a channel we have already joined
  @patch('irc.client.is_channel', return_value=True)
  def test_joined_channel(self, is_channel):
    self.client.channels.add(self.channel)

    self.client.join(self.channel)

    self.assertFalse(self.client._connect.called)
    self.assertFalse(self.client.connection.join.called)

  # check that we ignore requests for joining a channel that doesn't exist
  @patch('irc.client.is_channel', return_value=False)
  def test_not_a_channel(self, is_channel):
    self.client.join(self.channel)

    # we should simply ignore invalid channels
    self.assertNotIn(self.channel, self.client.channels)
    self.assertFalse(self.client.connection.join.called)

  # check that we properly join valid channels
  @patch('irc.client.is_channel', return_value=True)
  def test_default(self, is_channel):
    self.client.join(self.channel)

    self.assertIn(self.channel, self.client.channels)
    self.client.connection.join.assert_called_once_with(self.channel)

# IRCClient.leave
class TestIRCClientLeave(unittest.TestCase):

  def setUp(self):
    self.channel = "#foo"

    self.client = IRCClient(MagicMock())
    self.client.connection = MagicMock()
    self.client.channels.add(self.channel)

  # check that we don't do leave channels if not connected
  def test_not_connected(self):
    self.client.connection.is_connected = Mock(return_value=False)

    self.client.leave(self.channel)

    self.assertFalse(self.client.connection.part.called)

  # check that we ignore requests for leaving a channel we haven't joined
  def test_unjoined_channel(self):
    self.client.leave("bar")

    self.assertFalse(self.client.connection.part.called)

  # check that we ignore requests for leaving a channel that doesn't exist
  @patch('irc.client.is_channel', return_value=False)
  def test_not_a_channel(self, is_channel):
    self.client.leave(self.channel)

    # we should simply forget about an invalid channel
    self.assertNotIn(self.channel, self.client.channels)
    self.assertFalse(self.client.connection.part.called)

  # check that we part and forget about valid channels we joined
  @patch('irc.client.is_channel', return_value=True)
  def test_default(self, is_channel):
    self.client.leave(self.channel)

    self.assertNotIn(self.channel, self.client.channels)
    self.client.connection.part.assert_called_once_with(self.channel)

# IRCClient.on_welcome
class TestIRCClientOnWelcome(unittest.TestCase):

  def setUp(self):
    self.client = IRCClient(MagicMock())

  # check that we join channels and clean the autojoin list
  def test_autojoin(self):
    self.client.join = MagicMock()
    self.client.autojoin.add("foo")

    self.client.on_welcome(MagicMock(), MagicMock())

    self.assertEqual(len(self.client.autojoin), 0)
    self.client.join.assert_called_once_with("foo")

# IRCClient.on_join
class TestIRCClientOnJoin(unittest.TestCase):

  # just check that this doesn't explode
  def test_default(self):
    IRCClient(MagicMock()).on_join(MagicMock(), MagicMock())

# IRCClient.on_pubmsg
class TestIRCClientOnPubMsg(unittest.TestCase):

  def setUp(self):
    self.client = IRCClient(MagicMock())

  # check that the IRC events are turned into a channel and message and passed to the callback
  def test_default(self):
    # prepare a mock IRC event
    channel = "channel"
    message = "message"
    event = MagicMock()
    event.target = channel
    event.arguments = [message]

    # this should be called for each IRC message received
    self.client.call_on_pubmsg = MagicMock()

    self.client.on_pubmsg(MagicMock(), event)

    self.client.call_on_pubmsg.assert_called_once_with(channel, message)

# IRCClient.on_disconnect
class TestIRCClientDisconnect(unittest.TestCase):

  def setUp(self):
    self.client = IRCClient(MagicMock())

  # check that we reconnect after a disconnect
  def test_reconnect(self):
    self.client._connect = MagicMock()

    self.client.on_disconnect(MagicMock(), MagicMock())

    self.client._connect.assert_called_once_with()

  # check that we schedule re-joining all channels
  def test_autojoin(self):
    channels = ["foo", "bar"]
    self.client.channels = channels
    self.client._connect = MagicMock()

    self.client.on_disconnect(MagicMock(), MagicMock())

    self.assertEqual(self.client.autojoin, channels)
