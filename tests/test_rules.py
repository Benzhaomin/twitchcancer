#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from sanitwitcher.rules import *

messages = {
  'sentence': 'this is a long sentence but not too long',
  'oneemote': 'Kappa',
  'onechar': 'k',
  'oneword': 'Elephant',
  'short': 'lol',
  'emotesandwords': 'THIS Kappa IS Kappa WHAT Kappa I Kappa CALL Kappa MUSIC',
  'longsentence': 'this is a long sentence but so long that it\s too long this is a long sentence but so long that it\s too long this is a long sentence but so long that it\s too long',
  'caps': 'THATS A LOT OF Caps',
}

class TestRule(unittest.TestCase):
  
  # sanitwitcher.rules.Rule.__str__()
  # check that we get the class's name in the string representation
  def test_rule_str(self):
    self.assertEqual(str(Rule()), "Rule")

  # sanitwitcher.rules.Rule.broken()
  # check that the no-op Rule class allows everything
  def test_rule_broken(self):
    r = Rule()
    
    for m in messages:
      self.assertFalse(r.broken(m))

class TestMinimumWordCount(unittest.TestCase):
  
  # sanitwitcher.rules.MinimumWordCount.broken()
  def test_minimum_word_count_broken(self):
    r = MinimumWordCount()
    
    for k,v in messages.items():
      if k in ["sentence", "emotesandwords", "longsentence", "caps"]:
        self.assertFalse(r.broken(v))
      else:
        self.assertTrue(r.broken(v))

class TestMinimumMessageLength(unittest.TestCase):
  
  # sanitwitcher.rules.MinimumMessageLength.broken()
  def test_minimum_message_length_broken(self):
    r = MinimumMessageLength()
    
    for k,v in messages.items():
      if k == "onechar":
        self.assertTrue(r.broken(v))
      else:
        self.assertFalse(r.broken(v))

class TestMaximumMessageLength(unittest.TestCase):
  
  # sanitwitcher.rules.MaximumMessageLength.broken()
  def test_maximum_message_length_broken(self):
    r = MaximumMessageLength()
    
    for k,v in messages.items():
      if k == "longsentence":
        self.assertTrue(r.broken(v))
      else:
        self.assertFalse(r.broken(v))

# message must have a {ratio} of caps to characters maximum
class TestCapsRatio(unittest.TestCase):
  
  # sanitwitcher.rules.CapsRatio.broken()
  def test_caps_ratio_broken(self):
    r = CapsRatio()
    
    for k,v in messages.items():
      if k in ["caps", "emotesandwords"]:
        self.assertTrue(r.broken(v))
      else:
        self.assertFalse(r.broken(v))
  
class TestEmoteCount(unittest.TestCase):
  
  # sanitwitcher.rules.EmoteCount.count()
  def test_emote_count_count(self):
    self.assertEqual(EmoteCount.count('Kappa'), 1)
    self.assertEqual(EmoteCount.count('notanemote'), 0) 
    self.assertEqual(EmoteCount.count('Kappa KappaPride Keepo'), 3) 
  
  # sanitwitcher.rules.EmoteCount.broken()
  def test_emote_count_broken(self):
    r = EmoteCount()
    
    for k,v in messages.items():
      if k == "emotesandwords":
        self.assertTrue(r.broken(v))
      else:
        self.assertFalse(r.broken(v))
    
class TestEmoteRatio(unittest.TestCase):
  
  # sanitwitcher.rules.EmoteRatio.broken()
  def test_emote_ratio_broken(self):
    r = EmoteRatio()
    
    for k,v in messages.items():
      if k == "oneemote":
        self.assertTrue(r.broken(v))
      else:
        self.assertFalse(r.broken(v))
