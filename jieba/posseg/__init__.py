from __future__ import absolute_import, unicode_literals
import re
import os
import jieba
import sys
import marshal
from functools import wraps
from .._compat import *
from .viterbi import viterbi

PROB_START_P = "prob_start.p"
PROB_TRANS_P = "prob_trans.p"
PROB_EMIT_P = "prob_emit.p"
CHAR_STATE_TAB_P = "char_state_tab.p"

re_han_detail = re.compile("([\u4E00-\u9FA5]+)")
re_skip_detail = re.compile("([\.0-9]+|[a-zA-Z0-9]+)")
re_han_internal = re.compile("([\u4E00-\u9FA5a-zA-Z0-9+#&\._]+)")
re_skip_internal = re.compile("(\r\n|\s)")

re_eng = re.compile("[a-zA-Z0-9]+")
re_num = re.compile("[\.0-9]+")

re_eng1 = re.compile('^[a-zA-Z0-9]$', re.U)


def load_model(f_name, isJython=True):
    _curpath = os.path.normpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    result = {}
    with open(f_name, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            line = line.decode("utf-8")
            word, _, tag = line.split(" ")
            result[word] = tag

    if not isJython:
        return result

    start_p = {}
    abs_path = os.path.join(_curpath, PROB_START_P)
    with open(abs_path, 'rb') as f:
        start_p = marshal.load(f)

    trans_p = {}
    abs_path = os.path.join(_curpath, PROB_TRANS_P)
    with open(abs_path, 'rb') as f:
        trans_p = marshal.load(f)

    emit_p = {}
    abs_path = os.path.join(_curpath, PROB_EMIT_P)
    with open(abs_path, 'rb') as f:
        emit_p = marshal.load(f)

    state = {}
    abs_path = os.path.join(_curpath, CHAR_STATE_TAB_P)
    with open(abs_path, 'rb') as f:
        state = marshal.load(f)
    f.closed

    return state, start_p, trans_p, emit_p, result

if sys.platform.startswith("java"):
    char_state_tab_P, start_P, trans_P, emit_P, word_tag_tab = load_model(
        jieba.get_abs_path_dict())
else:
    from .char_state_tab import P as char_state_tab_P
    from .prob_start import P as start_P
    from .prob_trans import P as trans_P
    from .prob_emit import P as emit_P

    word_tag_tab = load_model(jieba.get_abs_path_dict(), isJython=False)


def makesure_userdict_loaded(fn):

    @wraps(fn)
    def wrapped(*args, **kwargs):
        if jieba.user_word_tag_tab:
            word_tag_tab.update(jieba.user_word_tag_tab)
            jieba.user_word_tag_tab = {}
        return fn(*args, **kwargs)

    return wrapped


class pair(object):

    def __init__(self, word, flag):
        self.word = word
        self.flag = flag

    def __unicode__(self):
        return '%s/%s' % (self.word, self.flag)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if PY2:
            return self.__unicode__().encode(default_encoding)
        else:
            return self.__unicode__()

    def encode(self, arg):
        return self.__unicode__().encode(arg)


def __cut(sentence):
    prob, pos_list = viterbi(
        sentence, char_state_tab_P, start_P, trans_P, emit_P)
    begin, nexti = 0, 0

    for i, char in enumerate(sentence):
        pos = pos_list[i][0]
        if pos == 'B':
            begin = i
        elif pos == 'E':
            yield pair(sentence[begin:i + 1], pos_list[i][1])
            nexti = i + 1
        elif pos == 'S':
            yield pair(char, pos_list[i][1])
            nexti = i + 1
    if nexti < len(sentence):
        yield pair(sentence[nexti:], pos_list[nexti][1])


def __cut_detail(sentence):
    blocks = re_han_detail.split(sentence)
    for blk in blocks:
        if re_han_detail.match(blk):
            for word in __cut(blk):
                yield word
        else:
            tmp = re_skip_detail.split(blk)
            for x in tmp:
                if x:
                    if re_num.match(x):
                        yield pair(x, 'm')
                    elif re_eng.match(x):
                        yield pair(x, 'eng')
                    else:
                        yield pair(x, 'x')


def __cut_DAG_NO_HMM(sentence):
    DAG = jieba.get_DAG(sentence)
    route = {}
    jieba.calc(sentence, DAG, route)
    x = 0
    N = len(sentence)
    buf = ''
    while x < N:
        y = route[x][1] + 1
        l_word = sentence[x:y]
        if re_eng1.match(l_word):
            buf += l_word
            x = y
        else:
            if buf:
                yield pair(buf, 'eng')
                buf = ''
            yield pair(l_word, word_tag_tab.get(l_word, 'x'))
            x = y
    if buf:
        yield pair(buf, 'eng')
        buf = ''


def __cut_DAG(sentence):
    DAG = jieba.get_DAG(sentence)
    route = {}

    jieba.calc(sentence, DAG, route)

    x = 0
    buf = ''
    N = len(sentence)
    while x < N:
        y = route[x][1] + 1
        l_word = sentence[x:y]
        if y - x == 1:
            buf += l_word
        else:
            if buf:
                if len(buf) == 1:
                    yield pair(buf, word_tag_tab.get(buf, 'x'))
                elif not jieba.FREQ.get(buf):
                    recognized = __cut_detail(buf)
                    for t in recognized:
                        yield t
                else:
                    for elem in buf:
                        yield pair(elem, word_tag_tab.get(elem, 'x'))
                buf = ''
            yield pair(l_word, word_tag_tab.get(l_word, 'x'))
        x = y

    if buf:
        if len(buf) == 1:
            yield pair(buf, word_tag_tab.get(buf, 'x'))
        elif not jieba.FREQ.get(buf):
            recognized = __cut_detail(buf)
            for t in recognized:
                yield t
        else:
            for elem in buf:
                yield pair(elem, word_tag_tab.get(elem, 'x'))


def __cut_internal(sentence, HMM=True):
    sentence = strdecode(sentence)
    blocks = re_han_internal.split(sentence)
    if HMM:
        __cut_blk = __cut_DAG
    else:
        __cut_blk = __cut_DAG_NO_HMM

    for blk in blocks:
        if re_han_internal.match(blk):
            for word in __cut_blk(blk):
                yield word
        else:
            tmp = re_skip_internal.split(blk)
            for x in tmp:
                if re_skip_internal.match(x):
                    yield pair(x, 'x')
                else:
                    for xx in x:
                        if re_num.match(xx):
                            yield pair(xx, 'm')
                        elif re_eng.match(x):
                            yield pair(xx, 'eng')
                        else:
                            yield pair(xx, 'x')


def __lcut_internal(sentence):
    return list(__cut_internal(sentence))


def __lcut_internal_no_hmm(sentence):
    return list(__cut_internal(sentence, False))


@makesure_userdict_loaded
def cut(sentence, HMM=True):
    if jieba.pool is None:
        for w in __cut_internal(sentence, HMM=HMM):
            yield w
    else:
        parts = strdecode(sentence).splitlines(True)
        if HMM:
            result = jieba.pool.map(__lcut_internal, parts)
        else:
            result = jieba.pool.map(__lcut_internal_no_hmm, parts)
        for r in result:
            for w in r:
                yield w
