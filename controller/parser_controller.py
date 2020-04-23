
import os

from lib import route
from model import parser_engine

@route.router(url=r"/", method=route.router._POST)
def cv_parser():
    filename = os.getcwd() + '/test/carjob/1.html'
    with open(filename, 'r') as f:
        fileContext = f.read()
        f.close()

        obj = parser_engine.ParserEngine(51, fileContext, 1)
        obj.dispatch()