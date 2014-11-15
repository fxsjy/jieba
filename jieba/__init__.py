__version__ = '0.34'
__license__ = 'MIT'

import re
import os
import sys
from . import finalseg
import time
import tempfile
import marshal
from math import log
import random
import threading
from functools import wraps
import logging
from hashlib import md5

DICTIONARY = "dict.txt"
DICT_LOCK = threading.RLock()
pfdict = None # to be initialized
FREQ = {}
min_freq = 0.0
total = 0.0
user_word_tag_tab = {}
initialized = False

log_console = logging.StreamHandler(sys.stderr)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(log_console)

def setLogLevel(log_level):
    global logger
    logger.setLevel(log_level)

def gen_pfdict(f_name):
    lfreq = {}
    pfdict = set()
    ltotal = 0.0
    with open(f_name, 'rb') as f:
        lineno = 0
        for line in f.read().rstrip().decode('utf-8').split('\n'):
            lineno += 1
            try:
                word,freq = line.split(' ')[:2]
                freq = float(freq)
                lfreq[word] = freq
                ltotal += freq
                for ch in range(len(word)):
                    pfdict.add(word[:ch+1])
            except ValueError as e:
                logger.debug('%s at line %s %s' % (f_name, lineno, line))
                raise e
    return pfdict, lfreq, ltotal

def initialize(dictionary=None):
    global pfdict, FREQ, total, min_freq, initialized, DICTIONARY, DICT_LOCK
    if not dictionary:
        dictionary = DICTIONARY
    with DICT_LOCK:
        if initialized:
            return
        if pfdict:
            del pfdict
            pfdict = None
        _curpath = os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

        abs_path = os.path.join(_curpath, dictionary)
        logger.debug("Building prefix dict from %s ..." % abs_path)
        t1 = time.time()
        if abs_path == os.path.join(_curpath, "dict.txt"): #default dictionary
            cache_file = os.path.join(tempfile.gettempdir(), "jieba.cache")
        else: #custom dictionary
            cache_file = os.path.join(tempfile.gettempdir(), "jieba.u%s.cache" % md5(abs_path.encode('utf-8', 'replace')).hexdigest())

        load_from_cache_fail = True
        if os.path.exists(cache_file) and os.path.getmtime(cache_file) > os.path.getmtime(abs_path):
            logger.debug("Loading model from cache %s" % cache_file)
            try:
                with open(cache_file, 'rb') as cf:
                    pfdict,FREQ,total,min_freq = marshal.load(cf)
                # prevent conflict with old version
                load_from_cache_fail = not isinstance(pfdict, set)
            except:
                load_from_cache_fail = True

        if load_from_cache_fail:
            pfdict,FREQ,total = gen_pfdict(abs_path)
            FREQ = dict((k,log(float(v)/total)) for k,v in FREQ.items()) #normalize
            min_freq = min(FREQ.values())
            logger.debug("Dumping model to file cache %s" % cache_file)
            try:
                fd, fpath = tempfile.mkstemp()
                with os.fdopen(fd, 'wb') as temp_cache_file:
                    marshal.dump((pfdict,FREQ,total,min_freq), temp_cache_file)
                if os.name == 'nt':
                    from shutil import move as replace_file
                else:
                    replace_file = os.rename
                replace_file(fpath, cache_file)
            except:
                logger.exception("Dump cache file failed.")

        initialized = True

        logger.debug("Loading model cost %s seconds." % (time.time() - t1))
        logger.debug("Prefix dict has been built succesfully.")


def require_initialized(fn):

    @wraps(fn)
    def wrapped(*args, **kwargs):
        global initialized
        if initialized:
            return fn(*args, **kwargs)
        else:
            initialize(DICTIONARY)
            return fn(*args, **kwargs)

    return wrapped


def __cut_all(sentence):
    dag = get_DAG(sentence)
    old_j = -1
    for k,L in dag.items():
        if len(L) == 1 and k > old_j:
            yield sentence[k:L[0]+1]
            old_j = L[0]
        else:
            for j in L:
                if j > k:
                    yield sentence[k:j+1]
                    old_j = j


def calc(sentence, DAG, idx, route):
    N = len(sentence)
    route[N] = (0.0, '')
    for idx in range(N-1, -1, -1):
        route[idx] = max((FREQ.get(sentence[idx:x+1],min_freq) + route[x+1][0], x) for x in DAG[idx])

@require_initialized
def get_DAG(sentence):
    global pfdict, FREQ
    DAG = {}
    N = len(sentence)
    for k in range(N):
        tmplist = []
        i = k
        frag = sentence[k]
        while i < N and frag in pfdict:
            if frag in FREQ:
                tmplist.append(i)
            i += 1
            frag = sentence[k:i+1]
        if not tmplist:
            tmplist.append(k)
        DAG[k] = tmplist
    return DAG

def __cut_DAG_NO_HMM(sentence):
    re_eng = re.compile(r'[a-zA-Z0-9]',re.U)
    DAG = get_DAG(sentence)
    route = {}
    calc(sentence, DAG, 0, route)
    x = 0
    N = len(sentence)
    buf = ''
    while x < N:
        y = route[x][1] + 1
        l_word = sentence[x:y]
        if re_eng.match(l_word) and len(l_word) == 1:
            buf += l_word
            x = y
        else:
            if buf:
                yield buf
                buf = ''
            yield l_word
            x = y
    if buf:
        yield buf
        buf = ''

def __cut_DAG(sentence):
    DAG = get_DAG(sentence)
    route = {}
    calc(sentence, DAG, 0, route=route)
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
                    yield buf
                    buf = ''
                else:
                    if (buf not in FREQ):
                        recognized = finalseg.cut(buf)
                        for t in recognized:
                            yield t
                    else:
                        for elem in buf:
                            yield elem
                    buf = ''
            yield l_word
        x = y

    if buf:
        if len(buf) == 1:
            yield buf
        elif (buf not in FREQ):
            recognized = finalseg.cut(buf)
            for t in recognized:
                yield t
        else:
            for elem in buf:
                yield elem

def cut(sentence, cut_all=False, HMM=True):
    '''The main function that segments an entire sentence that contains
    Chinese characters into seperated words.
    Parameter:
        - sentence: The str to be segmented.
        - cut_all: Model type. True for full pattern, False for accurate pattern.
        - HMM: Whether to use the Hidden Markov Model.
    '''
    if isinstance(sentence, bytes):
        try:
            sentence = sentence.decode('utf-8')
        except UnicodeDecodeError:
            sentence = sentence.decode('gbk', 'ignore')

    # \u4E00-\u9FA5a-zA-Z0-9+#&\._ : All non-space characters. Will be handled with re_han
    # \r\n|\s : whitespace characters. Will not be handled.

    if cut_all:
        re_han, re_skip = re.compile("([\u4E00-\u9FA5]+)", re.U), re.compile("[^a-zA-Z0-9+#\n]", re.U)
    else:
        re_han, re_skip = re.compile("([\u4E00-\u9FA5a-zA-Z0-9+#&\._]+)", re.U), re.compile("(\r\n|\s)", re.U)
    blocks = re_han.split(sentence)
    if cut_all:
        cut_block = __cut_all
    elif HMM:
        cut_block = __cut_DAG
    else:
        cut_block = __cut_DAG_NO_HMM
    for blk in blocks:
        if not blk:
            continue
        if re_han.match(blk):
            for word in cut_block(blk):
                yield word
        else:
            tmp = re_skip.split(blk)
            for x in tmp:
                if re_skip.match(x):
                    yield x
                elif not cut_all:
                    for xx in x:
                        yield xx
                else:
                    yield x

def cut_for_search(sentence, HMM=True):
    words = cut(sentence, HMM=HMM)
    for w in words:
        if len(w) > 2:
            for i in range(len(w)-1):
                gram2 = w[i:i+2]
                if gram2 in FREQ:
                    yield gram2
        if len(w) > 3:
            for i in range(len(w)-2):
                gram3 = w[i:i+3]
                if gram3 in FREQ:
                    yield gram3
        yield w

@require_initialized
def load_userdict(f):
    ''' Load personalized dict to improve detect rate.
    Parameter:
        - f : A plain text file contains words and their ocurrences.
    Structure of dict file:
    word1 freq1 word_type1
    word2 freq2 word_type2
    ...
    Word type may be ignored
    '''
    if isinstance(f, str):
        f = open(f, 'rb')
    content = f.read().decode('utf-8')
    line_no = 0
    for line in content.split("\n"):
        line_no += 1
        if not line.rstrip():
            continue
        tup = line.split(" ")
        word, freq = tup[0], tup[1]
        if freq.isdigit() is False:
            continue
        if line_no == 1:
            word = word.replace('\ufeff',"") #remove bom flag if it exists
        add_word(*tup)

@require_initialized
def add_word(word, freq, tag=None):
    global FREQ, pfdict, total, user_word_tag_tab
    FREQ[word] = log(float(freq) / total)
    if tag is not None:
        user_word_tag_tab[word] = tag.strip()
    for ch in range(len(word)):
        pfdict.add(word[:ch+1])

__ref_cut = cut
__ref_cut_for_search = cut_for_search

def __lcut(sentence):
    return list(__ref_cut(sentence, False))
def __lcut_no_hmm(sentence):
    return list(__ref_cut(sentence, False, False))
def __lcut_all(sentence):
    return list(__ref_cut(sentence, True))
def __lcut_for_search(sentence):
    return list(__ref_cut_for_search(sentence))


@require_initialized
def enable_parallel(processnum=None):
    global pool, cut, cut_for_search
    if os.name == 'nt':
        raise Exception("jieba: parallel mode only supports posix system")
    from multiprocessing import Pool, cpu_count
    if processnum is None:
        processnum = cpu_count()
    pool = Pool(processnum)

    def pcut(sentence,cut_all=False,HMM=True):
        parts = re.compile('([\r\n]+)').split(sentence)
        if cut_all:
            result = pool.map(__lcut_all, parts)
        elif HMM:
            result = pool.map(__lcut, parts)
        else:
            result = pool.map(__lcut_no_hmm, parts)
        for r in result:
            for w in r:
                yield w

    def pcut_for_search(sentence):
        parts = re.compile('([\r\n]+)').split(sentence)
        result = pool.map(__lcut_for_search, parts)
        for r in result:
            for w in r:
                yield w

    cut = pcut
    cut_for_search = pcut_for_search

def disable_parallel():
    global pool,cut,cut_for_search
    if 'pool' in globals():
        pool.close()
        pool = None
    cut = __ref_cut
    cut_for_search = __ref_cut_for_search

def set_dictionary(dictionary_path):
    global initialized, DICTIONARY
    with DICT_LOCK:
        abs_path = os.path.normpath(os.path.join(os.getcwd(), dictionary_path))
        if not os.path.exists(abs_path):
            raise Exception("jieba: path does not exist: " + abs_path)
        DICTIONARY = abs_path
        initialized = False

def get_abs_path_dict():
    _curpath = os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    abs_path = os.path.join(_curpath,DICTIONARY)
    return abs_path

def tokenize(unicode_sentence, mode="default", HMM=True):
    """Tokenize a sentence and yields tuples of (word, start, end)
    Parameter:
        - sentence: the str to be segmented.
        - mode: "default" or "search", "search" is for finer segmentation.
        - HMM: whether to use the Hidden Markov Model.
    """
    if not isinstance(unicode_sentence, str):
        raise Exception("jieba: the input parameter should be str.")
    start = 0
    if mode == 'default':
        for w in cut(unicode_sentence, HMM=HMM):
            width = len(w)
            yield (w, start, start+width)
            start += width
    else:
        for w in cut(unicode_sentence, HMM=HMM):
            width = len(w)
            if len(w) > 2:
                for i in range(len(w)-1):
                    gram2 = w[i:i+2]
                    if gram2 in FREQ:
                        yield (gram2, start+i, start+i+2)
            if len(w) > 3:
                for i in range(len(w)-2):
                    gram3 = w[i:i+3]
                    if gram3 in FREQ:
                        yield (gram3, start+i, start+i+3)
            yield (w, start, start+width)
            start += width
