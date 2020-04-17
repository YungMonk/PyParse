#!/usr/bin/python3.8
# -*- coding: utf-8 -*-


class my_route():

    def __init__(self):
        self.routes = {}

    def Router(self, route_str):
        def decorator(f):
            self.routes[route_str] = f
            return f

        return decorator

    def Serve(self, path):
        view_func = self.routes.get(path)

        if view_func:
            return view_func()
        else:
            raise ValueError(
                'Route "{}"" has not been registered'.format(path))


if __name__ == '__main__':
    route = my_route()

    @route.Router("/")
    def Hello():
        return "hello world"

    print(route.Serve("/"))
