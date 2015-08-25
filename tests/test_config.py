#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from twitchcancer.config import Config

defaults = {"level1": {"level2": {"level3": "value"}}}

# twitchcancer.config.Config.get()
class TestConfigGet(unittest.TestCase):

  def setUp(self):
    Config.config = defaults

  # check that missing keys return nothing
  def test_get_missing_key(self):
    self.assertEqual(Config.get("missing.key.is.missing"), {})

  # check that low-level/simple values are returned
  def test_get_single_value(self):
    self.assertEqual(Config.get("level1.level2.level3"), "value")

  # check that high-level/compound values are returned
  def test_get_compound_value(self):
    self.assertEqual(Config.get("level1.level2"), {"level3": "value"})

# twitchcancer.config.Config.update()
class TestConfigUpdate(unittest.TestCase):

  def setUp(self):
    Config.config = defaults

  # check that new values are merged in
  def test_update_single_value(self):
    Config.update({"level1": {"level2": {"level3": "merged"}}})
    self.assertEqual(Config.config['level1']['level2']['level3'], "merged")

  # check that existing values stay in there
  def test_update_existing_untouched(self):
    Config.update({})
    self.assertEqual(Config.config['level1']['level2']['level3'], "value")

  # check that unknown keys are ignored
  def test_update_ignore_unknown_key(self):
    Config.update({"level1": {"level2": {"unknown": "merged"}}})
    self.assertEqual('unknown' not in Config.config['level1']['level2'], True)

# twitchcancer.config.Config.defaults()
class TestConfigDefaults(unittest.TestCase):

  # check that new values are merged in
  def test_defaults_defaults(self):
    Config.defaults()
    self.assertEqual('expose' in Config.config, True)
    self.assertEqual('record' in Config.config, True)
    self.assertEqual('monitor' in Config.config, True)
    self.assertEqual('chat' in Config.config['monitor'], True)
    self.assertEqual('unknown' not in Config.config, True)
