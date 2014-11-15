import re
import os
from . import viterbi
import jieba
import sys
import marshal
from functools import wraps

default_encoding = sys.getfilesystemencoding()

PROB_START_P = "prob_start.p"
PROB_TRANS_P = "prob_trans.p"
PROB_EMIT_P = "prob_emit.p"
CHAR_STATE_TAB_P = "char_state_tab.p"

def load_model(f_name, isJython=True):
    _curpath = os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

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
    char_state_tab_P, start_P, trans_P, emit_P, word_tag_tab = load_model(jieba.get_abs_path_dict())
else:
    from . import char_state_tab, prob_start, prob_trans, prob_emit
    char_state_tab_P, start_P, trans_P, emit_P = char_state_tab.P, prob_start.P, prob_trans.P, prob_emit.P
    word_tag_tab = load_model(jieba.get_abs_path_dict(), isJython=False)

def makesure_userdict_loaded(fn):

    @wraps(fn)
    def wrapped(*args,**kwargs):
        if jieba.user_word_tag_tab:
            word_tag_tab.update(jieba.user_word_tag_tab)
            jieba.user_word_tag_tab = {}
        return fn(*args,**kwargs)

    return wrapped

class pair(object):
    def __init__(self,word,flag):
        self.word = word
        self.flag = flag

    def __unicode__(self):
        return '%s/%s' % (self.word, self.flag)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__unicode__().encode(default_encoding)

    def encode(self,arg):
        return self.__unicode__().encode(arg)

def __cut(sentence):
    prob, pos_list = viterbi.viterbi(sentence, char_state_tab_P, start_P, trans_P, emit_P)
    begin, next = 0, 0

    for i,char in enumerate(sentence):
        pos = pos_list[i][0]
        if pos == 'B':
            begin = i
        elif pos == 'E':
            yield pair(sentence[begin:i+1], pos_list[i][1])
            next = i+1
        elif pos == 'S':
            yield pair(char, pos_list[i][1])
            next = i+1
    if next < len(sentence):
        yield pair(sentence[next:], pos_list[next][1])

def __cut_detail(sentence):
    re_han, re_skip = re.compile("([\u4E00-\u9FA5]+)"), re.compile("([\.0-9]+|[a-zA-Z0-9]+)")
    re_eng, re_num = re.compile("[a-zA-Z0-9]+"), re.compile("[\.0-9]+")
    blocks = re_han.split(sentence)
    for blk in blocks:
        if re_han.match(blk):
            for word in __cut(blk):
                yield word
        else:
            tmp = re_skip.split(blk)
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
    jieba.calc(sentence, DAG, 0, route=route)
    x = 0
    N = len(sentence)
    buf = ''
    re_eng = re.compile('[a-zA-Z0-9]',re.U)
    while x < N:
        y = route[x][1]+1
        l_word = sentence[x:y]
        if re_eng.match(l_word) and len(l_word) == 1:
            buf += l_word
            x = y
        else:
            if buf:
                yield pair(buf,'eng')
                buf = ''
            yield pair(l_word, word_tag_tab.get(l_word, 'x'))
            x = y
    if buf:
        yield pair(buf,'eng')
        buf = ''

def __cut_DAG(sentence):
    DAG = jieba.get_DAG(sentence)
    route = {}

    jieba.calc(sentence,DAG,0,route=route)

    x = 0
    buf = ''
    N = len(sentence)
    while x < N:
        y = route[x][1]+1
        l_word = sentence[x:y]
        if y-x == 1:
            buf += l_word
        else:
            if buf:
                if len(buf) == 1:
                    yield pair(buf, word_tag_tab.get(buf, 'x'))
                    buf = ''
                else:
                    if (buf not in jieba.FREQ):
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
        elif (buf not in jieba.FREQ):
            recognized = __cut_detail(buf)
            for t in recognized:
                yield t
        else:
            for elem in buf:
                yield pair(elem, word_tag_tab.get(elem, 'x'))

def __cut_internal(sentence, HMM=True):
    if not isinstance(sentence, str):
        try:
            sentence = sentence.decode('utf-8')
        except UnicodeDecodeError:
            sentence = sentence.decode('gbk', 'ignore')
    re_han, re_skip = re.compile("([\u4E00-\u9FA5a-zA-Z0-9+#&\._]+)"), re.compile("(\r\n|\s)")
    re_eng, re_num = re.compile("[a-zA-Z0-9]+"), re.compile("[\.0-9]+")
    blocks = re_han.split(sentence)
    if HMM:
        __cut_blk = __cut_DAG
    else:
        __cut_blk = __cut_DAG_NO_HMM

    for blk in blocks:
        if re_han.match(blk):
            for word in __cut_blk(blk):
                yield word
        else:
            tmp = re_skip.split(blk)
            for x in tmp:
                if re_skip.match(x):
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
    return list(__cut_internal(sentence,False))


@makesure_userdict_loaded
def cut(sentence, HMM=True):
    if (not hasattr(jieba, 'pool')) or (jieba.pool is None):
        for w in __cut_internal(sentence, HMM=HMM):
            yield w
    else:
        parts = re.compile('([\r\n]+)').split(sentence)
        if HMM:
            result = jieba.pool.map(__lcut_internal, parts)
        else:
            result = jieba.pool.map(__lcut_internal_no_hmm, parts)
        for r in result:
            for w in r:
                yield w

