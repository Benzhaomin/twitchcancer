#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import unittest
from unittest.mock import patch, Mock, MagicMock

from twitchcancer.chat.irc.irc import IRC

# IRC.__init__
class TestIRCInit(unittest.TestCase):
  pass

# IRC.__lazy_init__
class TestIRCLazyInit(unittest.TestCase):
  pass

# IRC.__iter__
class TestIRCIter(unittest.TestCase):
  pass

# IRC.__next__
class TestIRCNext(unittest.TestCase):

  def setUp(self):
    self.client = IRC(None, None)

    def lazy_init(self):
      self.messages = MagicMock()
      self.messages.get = MagicMock(side_effect=["1", "2", "3"])

    self.client.__lazy_init__ = MagicMock(side_effect=lazy_init(self.client))

  # check that the several call to next() return messages in order
  def test_default(self):
    self.assertEqual(self.client.__next__(), "1")
    self.assertEqual(self.client.__next__(), "2")
    self.assertEqual(self.client.__next__(), "3")

# IRC.join
class TestIRCJoin(unittest.TestCase):
  pass

# IRC.leave
class TestIRCLeave(unittest.TestCase):
  pass

# IRC.__getattr__
class TestIRCGetAttr(unittest.TestCase):
  pass

# IRC._client_thread
class TestIRCClientThread(unittest.TestCase):
  pass

# IRC._on_pubmsg
class TestIRCOnPubMsg(unittest.TestCase):

  def setUp(self):
    self.client = IRC(None, None)

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
