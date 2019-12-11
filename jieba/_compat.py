# -*- coding: utf-8 -*-
import os
import sys
import imp
import logging

log_console = logging.StreamHandler(sys.stderr)
default_logger = logging.getLogger(__name__)
default_logger.setLevel(logging.DEBUG)

def setLogLevel(log_level):
    global logger
    default_logger.setLevel(log_level)

try:
    import pkg_resources
    get_module_res = lambda *res: pkg_resources.resource_stream(__name__,
                                                                os.path.join(*res))
except ImportError:
    get_module_res = lambda *res: open(os.path.normpath(os.path.join(
                            os.getcwd(), os.path.dirname(__file__), *res)), 'rb')

try:
    import paddle
    if paddle.__version__ == '1.6.1':
        import paddle.fluid as fluid
        import jieba.lac_small.predict as predict
except ImportError:
    pass

PY2 = sys.version_info[0] == 2

default_encoding = sys.getfilesystemencoding()

if PY2:
    text_type = unicode
    string_types = (str, unicode)

    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()

else:
    text_type = str
    string_types = (str,)
    xrange = range

    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())

def strdecode(sentence):
    if not isinstance(sentence, text_type):
        try:
            sentence = sentence.decode('utf-8')
        except UnicodeDecodeError:
            sentence = sentence.decode('gbk', 'ignore')
    return sentence

def resolve_filename(f):
    try:
        return f.name
    except AttributeError:
        return repr(f)


def check_paddle_install():
    is_paddle_installed =  False
    try:
        if imp.find_module('paddle') and paddle.__version__ == '1.6.1':
            is_paddle_installed = True
        elif paddle.__version__ != '1.6.1':
            is_paddle_installed = False
            default_logger.debug("Check the paddle version is not correct, subject\
            you to use command to install paddle: pip uninstall paddlepaddle(-gpu), \
            pip install paddlepaddle==1.6.1-tiny. Now, back to jieba basic cut......")
    except ImportError:
        default_logger.debug("Can not import paddle, back to jieba basic cut......")
        is_paddle_installed = False
    return is_paddle_installed