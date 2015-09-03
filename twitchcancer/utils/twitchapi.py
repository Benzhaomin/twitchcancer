#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib.request

import logging
logger = logging.getLogger(__name__)

class TwitchApi:

  @classmethod
  # returns chat properties for a channel
  def chat_properties(cls, channel):
    # URLs don't want #s
    channel = channel.replace("#", "")
    url = 'http://api.twitch.tv/api/channels/{0}/chat_properties'.format(channel)

    return cls._load_json(url)

  @classmethod
  # returns a list of the top 100 streams, sorted by viewer count
  def stream_list(cls):
    url = 'https://api.twitch.tv/kraken/streams/?limit=100'

    return cls._load_json(url)

  @classmethod
  # returns a dict filled with json returned from a request to the given url
  # returns None on any error
  def _load_json(cls, url):
    try:
      with urllib.request.urlopen(url) as response:
        binary = response.read()

        string = binary.decode()

        data = json.loads(string)

        return data
    except urllib.error.URLError as e:
      logger.warning("Twitch API request failed %s", e)
      return None
    except urllib.error.HTTPError as e:
      logger.warning("Twitch API request failed %s", e)
      return None
    except ValueError as e:
      logger.warning("Twitch API response was not json %s", e)
      return None
