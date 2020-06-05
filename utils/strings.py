import struct
import fcntl
import socket
from typing import (
    TypeVar, Iterator, Iterable, NoReturn, overload, Container,
    Sequence, MutableSequence, Mapping, MutableMapping, Tuple, List, Any, Dict, Callable, Generic,
    Set, AbstractSet, FrozenSet, MutableSet, Sized, Reversible, SupportsInt, SupportsFloat, SupportsAbs,
    SupportsComplex, IO, BinaryIO, Union,
    ItemsView, KeysView, ValuesView, ByteString, Optional, AnyStr, Type, Text,
    Protocol,
)
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def handle_entityref(self, name):
        self.fed.append('&%s;' % name)

    def handle_charref(self, name):
        self.fed.append('&#%s;' % name)

    def get_data(self):
        return ''.join(self.fed)


def _strip_once(value):
    """
    Internal tag stripping utility used by strip_tags.
    """
    s = MLStripper()
    s.feed(value)
    s.close()
    return s.get_data()


# 去除html文本中的所有标签
def strip_tags(value="") -> str:
    """Return the given HTML with all tags stripped."""
    # Note: in typical case this loop executes _strip_once once. Loop condition
    # is redundant, but helps to reduce number of executions of _strip_once.
    value = str(value)
    while '<' in value and '>' in value:
        new_value = _strip_once(value)
        if value.count('<') == new_value.count('<'):
            # _strip_once wasn't able to detect more tags.
            break
        value = new_value
    return value


def trim(args="", *extra) -> str:
    # 去除字符串首尾处的空白字符（或者其他字符）
    """Strip whitespace (or other characters) from the beginning and end of a string"""
    return args.strip(extra[0] if len(extra) else " \t\n\r\0\x0B")


def host_name() -> str:
    """Return the current host name."""
    return socket.gethostname()


def host_address() -> str:
    """Return the current host address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def rpc_params(request: dict, **header: Any) -> dict:
    """merge the params for rpc request."""
    ip = host_address()
    params = {
        "header": {
            'provider': 'grab',
            'ip': ip,
            'appid': 10,
            'user_ip': ip,
            'uid': 10,
            'product_name': 'cvparser',
        },
        "request": {}
    }

    params['header'] = dict(params['header'], **header)
    params['request'] = dict(params['request'], **request)

    return params


def salary_to_k(args:str, flag:str="") -> str:
    """Salary unit converted to thousand."""
    if '千' in flag or 'K' in flag:
        return '%.2f' % (int(args))
    elif '万' in flag or 'W' in flag:
        return '%.2f' % (int(args)*10)
    else:
        return '%.2f' % (int(args)*0.001)


if __name__ == "__main__":

    dict1 = {"name": "owen", "age": 18, "height": 150}
    dict2 = {"birthday": "1999-11-22", "height": 180}

    newdict = dict(dict1, **dict2)
    print(newdict)
