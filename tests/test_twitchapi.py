#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import unittest
from unittest.mock import patch, Mock, MagicMock

from twitchcancer.utils.twitchapi import TwitchApi

def get_opener(response_data):
  data = MagicMock()
  data.read = Mock(return_value=response_data)
  response = MagicMock()
  response.__enter__ = Mock(return_value=data)

  return MagicMock(return_value=response)

def raise_url_error(foo):
  raise urllib.error.URLError('reason')

def raise_http_error(foo):
  raise urllib.error.HTTPError('reason', 'code', 'msg', 'hdrs', 'fp')

# TwitchApi._load_json
class TestTwitchApiLoadJson(unittest.TestCase):

  # check that a valid json response is returned
  def test_json_response(self):
    mock_urlopen = get_opener(b'{"data": "foo"}')

    with patch('twitchcancer.utils.twitchapi.urllib.request.urlopen', mock_urlopen):
      result = TwitchApi._load_json("")

      self.assertEqual(result, {"data": "foo"})

  # check that a non-json response is handled correctly
  def test_nonjson_response(self):
    mock_urlopen = get_opener(b'<html>404</html>')

    with patch('twitchcancer.utils.twitchapi.urllib.request.urlopen', mock_urlopen):
      result = TwitchApi._load_json("")

      self.assertEqual(result, None)

  # check that url errors are handled
  @patch('twitchcancer.utils.twitchapi.urllib.request.urlopen', side_effect=raise_url_error)
  def test_url_error(self, urlopen):
    result = TwitchApi._load_json("")

    self.assertEqual(result, None)

  # check that http errors are handled
  @patch('twitchcancer.utils.twitchapi.urllib.request.urlopen', side_effect=raise_http_error)
  def test_http_error(self, urlopen):
    result = TwitchApi._load_json("")

    self.assertEqual(result, None)

# TwitchApi.chat_properties
class TestTwitchApiChatProperties(unittest.TestCase):

  # check that _load_json is called with a clean channel name
  @patch('twitchcancer.utils.twitchapi.TwitchApi._load_json', return_value=None)
  def test_channel_striping(self, _load_json):
    TwitchApi.chat_properties('#channel')

    self.assertEqual(_load_json.call_count, 1)
    self.assertIn('channel', _load_json.call_args[0][0].split('/'))

# TwitchApi.stream_list
class TestTwitchApiStreamList(unittest.TestCase):

  # check that we call _load_json
  @patch('twitchcancer.utils.twitchapi.TwitchApi._load_json', return_value=None)
  def test_default(self, _load_json):
    TwitchApi.stream_list()

    self.assertEqual(_load_json.call_count, 1)