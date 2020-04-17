#!/usr/bin/python3.8
# -*- coding: utf-8 -*-


class my_route():

    def __init__(self):
        self.routes = {}

    def router(self, route_str):
        def decorator(f):
            self.routes[route_str] = f
            return f

        return decorator

    def serve(self, path):
        view_func = self.routes.get(path)

        if view_func:
            return view_func()
        else:
            raise ValueError(
                'Route "{}"" has not been registered'.format(path))
