from pip._internal.utils import logging

from lib import route
from model.engine_for_html import hEngine
from model.engine_for_json import jEngine

logger = route.logger


class engine(object):

    @classmethod
    async def dispatch(cls, **kawge):
        if 'from_json_encode_result:' in kawge['body']:
            kawge['body'] = kawge['body'].replace(
                'from_json_encode_result:', '', 1
            )
            return await jEngine(**kawge).dispatch()
        else:
            return await hEngine(**kawge).dispatch()
