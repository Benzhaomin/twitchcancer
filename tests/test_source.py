#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch

from twitchcancer.source.source import Source
from twitchcancer.source.log import Log
from twitchcancer.source.irc import IRC
from twitchcancer.source.twitch import Twitch

messages = [
  'this is a long sentence but not too long',
  'Kappa',
  'k',
  'Elephant',
  'lol',
  'THIS Kappa IS Kappa WHAT Kappa I Kappa CALL Kappa MUSIC',
  'this is a long sentence but so long that it\s too long this is a long sentence but so long that it\s too long this is a long sentence but so long that it\s too long',
  'THATS A LOT OF Caps',
]

class TestSource(unittest.TestCase):
  
  # twitchcancer.source.Source.__init__()
  pass

class TestLog(unittest.TestCase):
  
  # twitchcancer.source.log.Log.__init__()
  def test_source_log_init(self):
    log = Log(messages)
    expected = messages
    actual = log.messages
    self.assertEqual(actual, expected)
    
  # twitchcancer.source.log.Log.__iter__()
  def test_source_log_iter(self):
    log = Log(messages)
    expected = messages
    actual = [m for m in log]
    self.assertEqual(actual, expected)

class TestIRC(unittest.TestCase):
  
  # twitchcancer.source.irc.IRC.__init__()
  def test_source_log_init(self):
    pass

class TestTwitch(unittest.TestCase):
  
  # twitchcancer.source.twitch.Twitch.__init__()
  def test_source_log_init(self):
    pass
