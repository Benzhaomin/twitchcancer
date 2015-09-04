#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, MagicMock

from twitchcancer.api.requesthandler import RequestHandler

# clean the singleton before and after ourselves
class RequestHandlerTestCase(unittest.TestCase):

  def setUp(self):
    RequestHandler._RequestHandler__instance = None

  def tearDown(self):
    RequestHandler._RequestHandler__instance = None

# RequestHandler.instance()
class TestRequestHandlerInstance(RequestHandlerTestCase):

  # check that we only create a single instance
  @patch('twitchcancer.api.requesthandler.RequestHandler.__new__', side_effect=RequestHandler.__new__)
  def test_default(self, new):
    RequestHandler.instance()
    RequestHandler.instance()

    self.assertEqual(new.call_count, 1)

# RequestHandler.handle()
class TestRequestHandlerHandle(RequestHandlerTestCase):

  # check that we get an empty response to unknown requests
  def test_unknown(self):
    result = RequestHandler.instance().handle(None)

    self.assertEqual(result, {})

  # check that we get an empty response to malformed requests
  def test_malformed(self):
    result = RequestHandler.instance().handle({'request': 'twitchcancer.search'})

    self.assertEqual(result, {})

  # check that we transmit calls to real requests
  @patch('twitchcancer.api.requesthandler.Storage.search', return_value=["forsenlol"])
  def test_malformed(self, search):
    result = RequestHandler.instance().handle({'request': 'twitchcancer.search', 'data': 'for'})

    self.assertEqual(result, ["forsenlol"])
