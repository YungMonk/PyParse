#!/usr/bin/python3.8
# -*- coding:utf-8 -*-

import unittest
from lib.route import my_route


class TestUnit(unittest.TestCase):
    def setUp(self):
        self.app = my_route()

    def test_valid_route(self):

        @self.app.router('/')
        def index():
            print('Hello World') 

        self.app.serve('/')

    def test_invalid_route(self):
        with self.assertRaises(ValueError):
            self.app.serve('/invalid')
