from __future__ import absolute_import, unicode_literals
__version__ = '0.36.2'
__license__ = 'MIT'

import re
import os
import sys
import time
import tempfile
import marshal
from math import log
import threading
from functools import wraps
import logging
from hashlib import md5
from ._compat import *
from . import finalseg

DICTIONARY = "dict.txt"
DICT_LOCK = threading.RLock()
FREQ = {}  # to be initialized
total = 0
user_word_tag_tab = {}
initialized = False
pool = None
tmp_dir = None

_curpath = os.path.normpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

log_console = logging.StreamHandler(sys.stderr)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(log_console)


def setLogLevel(log_level):
    global logger
    logger.setLevel(log_level)


def gen_pfdict(f_name):
    lfreq = {}
    ltotal = 0
    with open(f_name, 'rb') as f:
        lineno = 0
        for line in f.read().rstrip().decode('utf-8').splitlines():
            lineno += 1
            try:
                word, freq = line.split(' ')[:2]
                freq = int(freq)
                lfreq[word] = freq
                ltotal += freq
                for ch in xrange(len(word)):
                    wfrag = word[:ch + 1]
                    if wfrag not in lfreq:
                        lfreq[wfrag] = 0
            except ValueError as e:
                logger.debug('%s at line %s %s' % (f_name, lineno, line))
                raise e
    return lfreq, ltotal


def initialize(dictionary=None):
    global FREQ, total, initialized, DICTIONARY, DICT_LOCK, tmp_dir
    if not dictionary:
        dictionary = DICTIONARY
    with DICT_LOCK:
        if initialized:
            return

        abs_path = os.path.join(_curpath, dictionary)
        logger.debug("Building prefix dict from %s ..." % abs_path)
        t1 = time.time()
        # default dictionary
        if abs_path == os.path.join(_curpath, "dict.txt"):
            cache_file = os.path.join(tmp_dir if tmp_dir else tempfile.gettempdir(),"jieba.cache")
        else:  # custom dictionary
            cache_file = os.path.join(tmp_dir if tmp_dir else tempfile.gettempdir(),"jieba.u%s.cache" % md5(
                abs_path.encode('utf-8', 'replace')).hexdigest())

        load_from_cache_fail = True
        if os.path.isfile(cache_file) and os.path.getmtime(cache_file) > os.path.getmtime(abs_path):
            logger.debug("Loading model from cache %s" % cache_file)
            try:
                with open(cache_file, 'rb') as cf:
                    FREQ, total = marshal.load(cf)
                load_from_cache_fail = False
            except Exception:
                load_from_cache_fail = True

        if load_from_cache_fail:
            FREQ, total = gen_pfdict(abs_path)
            logger.debug("Dumping model to file cache %s" % cache_file)
            try:
                fd, fpath = tempfile.mkstemp()
                with os.fdopen(fd, 'wb') as temp_cache_file:
                    marshal.dump((FREQ, total), temp_cache_file)
                if os.name == 'nt':
                    from shutil import move as replace_file
                else:
                    replace_file = os.rename
                replace_file(fpath, cache_file)
            except Exception:
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
    for k, L in iteritems(dag):
        if len(L) == 1 and k > old_j:
            yield sentence[k:L[0] + 1]
            old_j = L[0]
        else:
            for j in L:
                if j > k:
                    yield sentence[k:j + 1]
                    old_j = j


def calc(sentence, DAG, route):
    N = len(sentence)
    route[N] = (0, 0)
    logtotal = log(total)
    for idx in xrange(N - 1, -1, -1):
        route[idx] = max((log(FREQ.get(sentence[idx:x + 1]) or 1) -
                          logtotal + route[x + 1][0], x) for x in DAG[idx])


@require_initialized
def get_DAG(sentence):
    global FREQ
    DAG = {}
    N = len(sentence)
    for k in xrange(N):
        tmplist = []
        i = k
        frag = sentence[k]
        while i < N and frag in FREQ:
            if FREQ[frag]:
                tmplist.append(i)
            i += 1
            frag = sentence[k:i + 1]
        if not tmplist:
            tmplist.append(k)
        DAG[k] = tmplist
    return DAG

re_eng = re.compile('[a-zA-Z0-9]', re.U)


def __cut_DAG_NO_HMM(sentence):
    DAG = get_DAG(sentence)
    route = {}
    calc(sentence, DAG, route)
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
    calc(sentence, DAG, route=route)
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
                    yield buf
                    buf = ''
                else:
                    if not FREQ.get(buf):
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
        elif not FREQ.get(buf):
            recognized = finalseg.cut(buf)
            for t in recognized:
                yield t
        else:
            for elem in buf:
                yield elem

re_han_default = re.compile("([\u4E00-\u9FA5a-zA-Z0-9+#&\._]+)", re.U)
re_skip_default = re.compile("(\r\n|\s)", re.U)
re_han_cut_all = re.compile("([\u4E00-\u9FA5]+)", re.U)
re_skip_cut_all = re.compile("[^a-zA-Z0-9+#\n]", re.U)


def cut(sentence, cut_all=False, HMM=True):
    '''
    The main function that segments an entire sentence that contains
    Chinese characters into seperated words.

    Parameter:
        - sentence: The str(unicode) to be segmented.
        - cut_all: Model type. True for full pattern, False for accurate pattern.
        - HMM: Whether to use the Hidden Markov Model.
    '''
    sentence = strdecode(sentence)

    # \u4E00-\u9FA5a-zA-Z0-9+#&\._ : All non-space characters. Will be handled with re_han
    # \r\n|\s : whitespace characters. Will not be handled.

    if cut_all:
        re_han = re_han_cut_all
        re_skip = re_skip_cut_all
    else:
        re_han = re_han_default
        re_skip = re_skip_default
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
    """
    Finer segmentation for search engines.
    """
    words = cut(sentence, HMM=HMM)
    for w in words:
        if len(w) > 2:
            for i in xrange(len(w) - 1):
                gram2 = w[i:i + 2]
                if FREQ.get(gram2):
                    yield gram2
        if len(w) > 3:
            for i in xrange(len(w) - 2):
                gram3 = w[i:i + 3]
                if FREQ.get(gram3):
                    yield gram3
        yield w


@require_initialized
def load_userdict(f):
    '''
    Load personalized dict to improve detect rate.

    Parameter:
        - f : A plain text file contains words and their ocurrences.

    Structure of dict file:
    word1 freq1 word_type1
    word2 freq2 word_type2
    ...
    Word type may be ignored
    '''
    if isinstance(f, string_types):
        f = open(f, 'rb')
    content = f.read().decode('utf-8').lstrip('\ufeff')
    line_no = 0
    for line in content.splitlines():
        try:
            line_no += 1
            line = line.strip()
            if not line:
                continue
            tup = line.split(" ")
            add_word(*tup)
        except Exception as e:
            logger.debug('%s at line %s %s' % (f_name, lineno, line))
            raise e


@require_initialized
def add_word(word, freq=None, tag=None):
    """
    Add a word to dictionary.

    freq and tag can be omitted, freq defaults to be a calculated value
    that ensures the word can be cut out.
    """
    global FREQ, total, user_word_tag_tab
    word = strdecode(word)
    if freq is None:
        freq = suggest_freq(word, False)
    else:
        freq = int(freq)
    FREQ[word] = freq
    total += freq
    if tag is not None:
        user_word_tag_tab[word] = tag
    for ch in xrange(len(word)):
        wfrag = word[:ch + 1]
        if wfrag not in FREQ:
            FREQ[wfrag] = 0


def del_word(word):
    """
    Convenient function for deleting a word.
    """
    add_word(word, 0)


@require_initialized
def suggest_freq(segment, tune=False):
    """
    Suggest word frequency to force the characters in a word to be
    joined or splitted.

    Parameter:
        - segment : The segments that the word is expected to be cut into,
                    If the word should be treated as a whole, use a str.
        - tune : If True, tune the word frequency.

    Note that HMM may affect the final result. If the result doesn't change,
    set HMM=False.
    """
    ftotal = float(total)
    freq = 1
    if isinstance(segment, string_types):
        word = segment
        for seg in cut(word, HMM=False):
            freq *= FREQ.get(seg, 1) / ftotal
        freq = max(int(freq*total) + 1, FREQ.get(word, 1))
    else:
        segment = tuple(map(strdecode, segment))
        word = ''.join(segment)
        for seg in segment:
            freq *= FREQ.get(seg, 1) / ftotal
        freq = min(int(freq*total), FREQ.get(word, 0))
    if tune:
        add_word(word, freq)
    return freq


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

    def pcut(sentence, cut_all=False, HMM=True):
        parts = strdecode(sentence).splitlines(True)
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
        parts = strdecode(sentence).splitlines(True)
        result = pool.map(__lcut_for_search, parts)
        for r in result:
            for w in r:
                yield w

    cut = pcut
    cut_for_search = pcut_for_search


def disable_parallel():
    global pool, cut, cut_for_search
    if pool:
        pool.close()
        pool = None
    cut = __ref_cut
    cut_for_search = __ref_cut_for_search


def set_dictionary(dictionary_path):
    global initialized, DICTIONARY
    with DICT_LOCK:
        abs_path = os.path.normpath(os.path.join(os.getcwd(), dictionary_path))
        if not os.path.isfile(abs_path):
            raise Exception("jieba: file does not exist: " + abs_path)
        DICTIONARY = abs_path
        initialized = False


def get_abs_path_dict():
    return os.path.join(_curpath, DICTIONARY)


def tokenize(unicode_sentence, mode="default", HMM=True):
    """
    Tokenize a sentence and yields tuples of (word, start, end)

    Parameter:
        - sentence: the str(unicode) to be segmented.
        - mode: "default" or "search", "search" is for finer segmentation.
        - HMM: whether to use the Hidden Markov Model.
    """
    if not isinstance(unicode_sentence, text_type):
        raise Exception("jieba: the input parameter should be unicode.")
    start = 0
    if mode == 'default':
        for w in cut(unicode_sentence, HMM=HMM):
            width = len(w)
            yield (w, start, start + width)
            start += width
    else:
        for w in cut(unicode_sentence, HMM=HMM):
            width = len(w)
            if len(w) > 2:
                for i in xrange(len(w) - 1):
                    gram2 = w[i:i + 2]
                    if FREQ.get(gram2):
                        yield (gram2, start + i, start + i + 2)
            if len(w) > 3:
                for i in xrange(len(w) - 2):
                    gram3 = w[i:i + 3]
                    if FREQ.get(gram3):
                        yield (gram3, start + i, start + i + 3)
            yield (w, start, start + width)
            start += width
