#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.api.pubsubtopic import PubSubTopic, PubSubVariableTopic

# clean the singleton before and after ourselves
class PubSubTopicTestCase(unittest.TestCase):

  def setUp(self):
    PubSubTopic.instances.clear()

  def tearDown(self):
    PubSubTopic.instances.clear()

# PubSubTopic.instances
class TestPubSubTopicInstances(PubSubTopicTestCase):

  # check that PubSubTopic instances are stored in the class
  def test_instances(self):
    topic = PubSubTopic("foo", None, None)

    self.assertEqual(len(PubSubTopic.instances), 1)
    self.assertEqual(PubSubTopic.instances.pop(), topic)

  # check that duplicate instances are ignored
  def test_duplicate_instances(self):
    PubSubTopic("foo", "bar", None)
    PubSubTopic("foo", "baz", None)

    self.assertEqual(len(PubSubTopic.instances), 1)

# PubSubTopic.__init__
class TestPubSubTopicInit(PubSubTopicTestCase):

  # check that init stores values its passed
  def test_init(self):
    topic = PubSubTopic(name="foo", callback="bar", sleep="baz")

    self.assertEqual(topic.name, "foo")
    self.assertEqual(topic.callback, "bar")
    self.assertEqual(topic.sleep, "baz")
    self.assertEqual(topic.data, None)

# PubSubTopic.__str__
class TestPubSubTopicStr(PubSubTopicTestCase):

  # check that a PubSubTopic is stringified as its name
  def test_str(self):
    topic = PubSubTopic("foo", None, None)

    self.assertEqual(str(topic), "foo")

# PubSubTopic.__eq__
class TestPubSubTopicEq(PubSubTopicTestCase):

  # check that equality is based on the name
  def test_eq(self):
    foo1 = PubSubTopic("foo", None, None)
    foo2 = PubSubTopic("foo", None, None)
    bar = PubSubTopic("bar", None, None)

    self.assertTrue(foo1 == foo2)
    self.assertFalse(foo1 == bar)

# PubSubTopic.__neq__
class TestPubSubTopicNeq(PubSubTopicTestCase):

  # check that equality is based on the name
  def test_neq(self):
    foo1 = PubSubTopic("foo", None, None)
    foo2 = PubSubTopic("foo", None, None)
    bar = PubSubTopic("bar", None, None)

    self.assertFalse(foo1 != foo2)
    self.assertTrue(foo1 != bar)

# PubSubTopic.__hash__
class TestPubSubTopicHash(PubSubTopicTestCase):

  # check that hashing is based on the name
  def test_hash(self):
    foo = PubSubTopic("foo", None, None)

    self.assertEqual(hash(foo), hash(foo.name))

# PubSubTopic.find
class TestPubSubTopicFind(PubSubTopicTestCase):

  # check that an existing topic is found
  def test_exists(self):
    topic = PubSubTopic("foo", None, None)

    self.assertEqual(PubSubTopic.find("foo"), topic)

  # check that an unexisting topic is not found
  def test_not_exists(self):
    self.assertEqual(PubSubTopic.find("foobar"), None)

# PubSubTopic.match
class TestPubSubTopicMatch(PubSubTopicTestCase):

  # check that match compares the name only
  def test_match(self):
    topic = PubSubTopic("foo", None, None)

    self.assertTrue(topic.match("foo"))
    self.assertFalse(topic.match("bar"))

# PubSubTopic.payload
class TestPubSubTopicPayload(PubSubTopicTestCase):

  # check that the payload is computed when useCache is false and there's no cached data
  def test_payload_no_cache_no_data(self):
    callback = MagicMock(return_value="computed")
    topic = PubSubTopic("no_cache_no_data", callback, None)

    payload = topic.payload(False)

    callback.assert_called_once_with()
    self.assertEqual(payload, "computed")

  # check that the payload is computed when useCache is false even when there's cached data
  def test_payload_no_cache_with_data(self):
    callback = MagicMock(return_value="computed")
    topic = PubSubTopic("no_cache_with_data", callback, None)

    topic.data = "cached"
    payload = topic.payload(False)

    callback.assert_called_once_with()
    self.assertEqual(payload, "computed")

  # check that the payload is computed when useCache is true but there's no cached data
  def test_payload_with_cache_no_data(self):
    callback = MagicMock(return_value="computed")
    topic = PubSubTopic("with_cache_no_data", callback, None)

    topic.data = None
    payload = topic.payload(True)

    callback.assert_called_once_with()
    self.assertEqual(payload, "computed")

  # check that the payload is not computed when useCache is true and there is cached data
  def test_payload_with_cache_with_data(self):
    callback = MagicMock(return_value="computed")
    topic = PubSubTopic("with_cache_with_data", callback, None)

    topic.data = "cached"
    payload = topic.payload(True)

    self.assertFalse(callback.called)
    self.assertEqual(payload, "cached")

# PubSubVariableTopic.__init__
class TestPubSubVariableTopicInit(PubSubTopicTestCase):

  # check that init stores values its passed
  def test_init_members(self):
    topic = PubSubVariableTopic(name="foo.*", callback="bar", sleep="baz")

    self.assertEqual(topic.name, "foo")
    self.assertEqual(topic.callback, "bar")
    self.assertEqual(topic.sleep, "baz")
    self.assertEqual(topic.data, {})

  # check that init refuses variable topics without variable part
  def test_init_members(self):
    for name in ["foo", "foo.bar", "*.foo", "*", ".*"]:
      self.assertRaises(NotImplementedError, lambda: PubSubVariableTopic(name=name, callback="bar", sleep="baz"))

# PubSubVariableTopic.match
class TestPubSubVariableTopicMatch(PubSubTopicTestCase):

  # check that match compares the name only
  def test_match(self):
    topic = PubSubVariableTopic("match.*", None, None)

    self.assertTrue(topic.match("match.foo"))
    self.assertTrue(topic.match("match.bar.baz"))
    self.assertFalse(topic.match("match"))
    self.assertFalse(topic.match("foo"))

  # check we extract the variable part correctly
  def test_argument(self):
    topic = PubSubVariableTopic("arg.*", None, None)

    self.assertEqual(topic.argument("arg.foo"), "foo")

# PubSubVariableTopic.payload
class TestPubSubVariableTopicPayload(PubSubTopicTestCase):

  # check that the payload is computed when useCache is false and there's no cached data
  def test_payload_no_cache_no_data(self):
    callback = MagicMock(return_value="computed")
    topic = PubSubVariableTopic("no_cache_no_data.*", callback, None)

    variable = "no_cache_no_data.foo"
    payload = topic.payload(False, name=variable)

    callback.assert_called_once_with("foo")
    self.assertEqual(payload, "computed")

  # check that the payload is computed when useCache is false even when there's cached data
  def test_payload_no_cache_with_data(self):
    callback = MagicMock(return_value="computed")
    topic = PubSubVariableTopic("no_cache_with_data.*", callback, None)

    variable = "no_cache_with_data.foo"
    topic.data[variable] = "cached"
    payload = topic.payload(False, name=variable)

    callback.assert_called_once_with("foo")
    self.assertEqual(payload, "computed")

  # check that the payload is computed when useCache is true but there's no cached data
  def test_payload_with_cache_no_data(self):
    callback = MagicMock(return_value="computed")
    topic = PubSubVariableTopic("with_cache_no_data.*", callback, None)

    variable = "with_cache_no_data.foo"
    payload = topic.payload(True, name=variable)

    callback.assert_called_once_with("foo")
    self.assertEqual(payload, "computed")

  # check that the payload is not computed when useCache is true and there is cached data
  def test_payload_with_cache_with_data(self):
    callback = MagicMock(return_value="computed")
    topic = PubSubVariableTopic("with_cache_with_data.*", callback, None)

    variable = "test_payload_with_cache_with_data.foo"
    topic.data[variable] = "cached"
    payload = topic.payload(True, name=variable)

    self.assertFalse(callback.called)
    self.assertEqual(payload, "cached")
