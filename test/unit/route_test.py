#!/usr/bin/python3.8
# -*- coding:utf-8 -*- 🂡🂢🂣🂤🂥🂦🂧🂨🂩🂪🂫🂬🂭🂮🂱🂲🂳🂴🂵🂶🂷🂸🂹🂺🂻🂼🂽🂾🃁🃂🃃🃄🃅🃆🃇🃈🃉🃊🃋🃌🃍🃎🃑🃒🃓🃔🃕🃖🃗🃘🃙🃚🃛🃜🃝🃞

import unittest
from lib.route import router


class TestUnit(unittest.TestCase):
    def setUp(self):
        self.app = router()

    def test_valid_route(self):

        @self.app.route(url = r'/')
        def index():
            print('Hello World')

    def test_invalid_route(self):
        with self.assertRaises(ValueError):
            self.app.route(url=r'/invalid')
