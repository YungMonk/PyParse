#!/usr/bin/python3.8
# -*- coding:utf-8 -*-

import unittest
from lib.route import my_route


class TestNotFlask(unittest.TestCase):
    def setUp(self):
        self.app = my_route()

    def test_valid_route(self):

        @self.app.Router('/')
        def index():
            return 'Hello World'

        self.assertEqual(self.app.Serve('/'), 'Hello World')

    def test_invalid_route(self):
        with self.assertRaises(ValueError):
            self.app.Serve('/invalid')
