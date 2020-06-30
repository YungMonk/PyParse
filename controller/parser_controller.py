
import os
import time

from tornado.web import HTTPError

from lib import route, path
from model.engine import engine as eng
from config import static_param


class HelloTest(object):

    @route.router.route(url=r"/hello", method=route.router._POST | route.router._GET)
    async def home(self, req):
        return "hello world"

    @route.router.route(url=r"/parse", method=route.router._POST | route.router._GET)
    async def cv_parser(self, req):
        if 'request' not in req.json_args:
            raise HTTPError(100001, "Params is error, 'request' not found.")

        if 'p' not in req.json_args['request']:
            raise HTTPError(100001, "Params is error, 'request.p' not found.")

        if 'body' not in req.json_args['request']['p']:
            raise HTTPError(100001, "Params is error, 'request.p.body' not found.")

        if 'type' not in req.json_args['request']['p']:
            raise HTTPError(100001, "Params is error, 'request.p.type' not found.")

        if 'site_id' not in req.json_args['request']['p']:
            raise HTTPError(100001, "Params is error, 'request.p.site_id' not found.")

        if req.json_args['request']['p']['site_id'] not in static_param.channelMap:
            raise HTTPError(100002, "Params is error, site_id is no support!")

        if req.json_args['request']['p']['type'] not in static_param.parserType:
            raise HTTPError(100002, "Params is error, type is no support!")

        return await eng.dispatch(**req.json_args['request']['p'])