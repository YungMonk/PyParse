
import os
import time

from lib import route, path
from model import parser_engine
from config import static_param


class HelloTest(object):

    @route.router.route(url=r"/hello", method=route.router._POST | route.router._GET)
    async def home(self, req):
        return "hello world"

    @route.router.route(url=r"/parse", method=route.router._POST | route.router._GET)
    async def cv_parser(self, req):

        if 'request' not in req.json_args:
            return '{"code":1000,"message":"params is error, \'request is not exist!\'"}'

        if 'p' not in req.json_args['request']:
            return '{"code":1000,"message":"params is error, \'p is not exist!\'"}'

        if 'body' not in req.json_args['request']['p']:
            return '{"code":1000,"message":"params is error, \'body is not exist!\'"}'

        if 'type' not in req.json_args['request']['p']:
            return '{"code":1000,"message":"params is error, \'type is not exist!\'"}'

        if 'site_id' not in req.json_args['request']['p']:
            return '{"code":1000,"message":"params is error, \'site_id is not exist!\'"}'

        if req.json_args['request']['p']['site_id'] not in static_param.channelMap:
            return '{"code":1000,"message":"params is error, \'site_id is no availd!\'"}'

        if req.json_args['request']['p']['type'] not in static_param.parserType:
            return '{"code":1000,"message":"params is error, \'type is no availd!\'"}'

        return parser_engine.ParserEngine(**req.json_args['request']['p']).dispatch()
