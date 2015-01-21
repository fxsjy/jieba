from __future__ import with_statement
__version__ = '0.35'
__license__ = 'MIT'

import re
import os
import sys
import finalseg
import time
import tempfile
import marshal
from math import log
import random
import threading
from functools import wraps
import logging
from hashlib import md5
import sqlite3

DICTIONARY = "dict.txt"
DICT_LOCK = threading.RLock()
pfdict = None # to be initialized
FREQ = {}
min_freq = 0.0
total = 0.0
user_word_tag_tab = {}
initialized = False
use_sqlite = False

log_console = logging.StreamHandler(sys.stderr)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(log_console)

def setLogLevel(log_level):
    global logger
    logger.setLevel(log_level)

def gen_pfdict(f_name):
    global use_sqlite

    if not use_sqlite :
        lfreq = {}
        pfdict = set()
    else :
        use_sqlite["db"].isolation_level = None
        # We are just building a one-time on-disk cache,
        # so we don't need an in-memory sqlite cache right now.
        use_sqlite["conn"].execute('PRAGMA cache_size=1')
        use_sqlite["conn"].execute("begin")
        logger.debug("Making first-pass over sqlite cache...")

    ltotal = 0.0
    with open(f_name, 'rb', 0) as f:
        lineno = 0
        while True :
            line = f.readline().rstrip().decode('utf-8')
            if line == u'' :
                break
            lineno += 1
            try:
                word,freq = line.split(' ')[:2]
                freq = float(freq)
                if not use_sqlite :
                    lfreq[word] = freq
                else :
                    try :
                        use_sqlite["conn"].execute("insert into FREQ values (?, ?)", (word, freq))
                    except sqlite3.IntegrityError, e :
                        use_sqlite["conn"].execute("replace into FREQ values (?, ?)", (word, freq))
                ltotal += freq
                for ch in xrange(len(word)):
                    sub_word = word[:ch+1]
                    if not use_sqlite :
                        pfdict.add(sub_word)
                    else :
                        use_sqlite["conn"].execute("insert into pfdict values (?)", (sub_word,))

            except ValueError, e:
                logger.debug('%s at line %s %s' % (f_name, lineno, line))
                raise ValueError, e

    if not use_sqlite :
        FREQ = dict((k,log(float(v)/ltotal)) for k,v in lfreq.iteritems()) #normalize
        gen_min_freq = min(FREQ.itervalues())
        return pfdict, FREQ, ltotal, gen_min_freq
    else :
        # If we use "UPDATE TABLE" to normalize, the resulting database file size
        # on disk is 45 megabytes, but if we create a new table
        # and drop the old table then it is only 32 megabytes...strange.

        use_sqlite["conn"].execute("commit")
        use_sqlite["conn"].execute("begin")
        tmp_cursor = use_sqlite["db"].cursor()
        logger.debug("Getting sqlite frequencies.")
        rs = tmp_cursor.execute("select * from FREQ")
        gen_min_freq = False
        ncount = 0
        while True :
            result = rs.fetchone()
            if result is None :
                break
            ncount += 1
            word = result[0]
            freq = result[1]
            norm_freq = log(float(freq) / ltotal)
            use_sqlite["conn"].execute("update FREQ set freq = ? where word = ?", (word, norm_freq))
            if not gen_min_freq or norm_freq < gen_min_freq :
                gen_min_freq = norm_freq

        logger.debug("Normalized %s values." % ncount)

        use_sqlite["conn"].execute("insert into FREQ values ('total', ?)", (ltotal,))
        use_sqlite["conn"].execute("insert into FREQ values ('min_freq', ?)", (gen_min_freq,))
        use_sqlite["conn"].execute("commit")
        use_sqlite["conn"].execute("vacuum")
        # Back to default cache_size. About 8MB.
        # Maybe this can be configured dynamically.
        use_sqlite["conn"].execute('PRAGMA cache_size=2000')
        return False, False, ltotal, gen_min_freq

def init_sqlite(cache_file) :
    global use_sqlite
    db = sqlite3.connect(cache_file)
    conn = db.cursor()
    conn.execute('pragma journal_mode=OFF')
    conn.execute('PRAGMA synchronous=OFF')
    use_sqlite = {"conn" : conn, "db" : db}
    conn.execute("create table if not exists pfdict (word text)")
    conn.execute("create index if not exists pfdict_index on pfdict (word)")
    conn.execute("create table if not exists FREQ (word text primary key, freq real)")

# 'sqlite' can be True or '/path/to/jieba{hash}.db' as cache
# if True, then use /tmp as usual
def initialize(dictionary=None, sqlite = False):
    global pfdict, FREQ, total, min_freq, initialized, DICTIONARY, DICT_LOCK, use_sqlite
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

        load_from_cache_fail = True

        if not sqlite :
            if abs_path == os.path.join(_curpath, "dict.txt"): #default dictionary
                cache_file = os.path.join(tempfile.gettempdir(), "jieba.cache")
            else: #custom dictionary
                cache_file = os.path.join(tempfile.gettempdir(), "jieba.u%s.cache" % md5(abs_path.encode('utf-8', 'replace')).hexdigest())
        else :
            if isinstance(sqlite, str) :
                cache_file = sqlite
            else :
                cache_file = os.path.join(tempfile.gettempdir(), "jieba.u%s.db" % md5(abs_path.encode('utf-8', 'replace')).hexdigest())

            init_sqlite(cache_file)

        if os.path.exists(cache_file) and os.path.getmtime(cache_file) > os.path.getmtime(abs_path):
            logger.debug("Loading model from cache %s" % cache_file)
            if not sqlite :
                try:
                    with open(cache_file, 'rb') as cf:
                        pfdict,FREQ,total,min_freq = marshal.load(cf)
                    # prevent conflict with old version
                    load_from_cache_fail = not isinstance(pfdict, set)
                except:
                    load_from_cache_fail = True
            else :
                rs = use_sqlite["conn"].execute("select * from FREQ where word = 'total'")
                result = rs.fetchone()
                if result is not None :
                    total = result[1]
                    rs = use_sqlite["conn"].execute("select * from FREQ where word = 'min_freq'")
                    result = rs.fetchone()
                    if result is not None :
                        min_freq = result[1]
                        load_from_cache_fail = False
        else :
            # Throw old one if stale. In-memory version can just over-write on open('wb')
            if sqlite and os.path.exists(cache_file) :
                os.unlink(cache_file)
                init_sqlite(cache_file)

        if load_from_cache_fail:
            pfdict,FREQ,total,min_freq = gen_pfdict(abs_path)
            if not sqlite :
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
    for k,L in dag.iteritems():
        if len(L) == 1 and k > old_j:
            yield sentence[k:L[0]+1]
            old_j = L[0]
        else:
            for j in L:
                if j > k:
                    yield sentence[k:j+1]
                    old_j = j


def calc(sentence, DAG, route):
    N = len(sentence)
    route[N] = (0.0, '')
    for idx in xrange(N-1, -1, -1):
        route[idx] = max((in_FREQ(sentence[idx:x+1],min_freq) + route[x+1][0], x) for x in DAG[idx])

def in_FREQ(word, default = False) :
    if not use_sqlite :
        return FREQ[word] if word in FREQ else default 
    else :
        result = use_sqlite["conn"].execute("select * from FREQ where word = ?", (word,)).fetchone()
        return result[1] if result is not None else default 

@require_initialized
def get_DAG(sentence):
    global pfdict, FREQ
    DAG = {}
    N = len(sentence)
    for k in xrange(N):
        tmplist = []
        i = k
        frag = sentence[k]
        while i < N :
            if not use_sqlite :
                if frag not in pfdict:
                    break
            else :
                result = use_sqlite["conn"].execute("select * from pfdict where word = ?", (frag,)).fetchone()
                if result is None :
                    break

            if in_FREQ(frag) :
               tmplist.append(i)

            i += 1
            frag = sentence[k:i+1]
        if not tmplist:
            tmplist.append(k)
        DAG[k] = tmplist
    return DAG

def __cut_DAG_NO_HMM(sentence):
    re_eng = re.compile(ur'[a-zA-Z0-9]',re.U)
    DAG = get_DAG(sentence)
    route = {}
    calc(sentence, DAG, route)
    x = 0
    N = len(sentence)
    buf = u''
    while x < N:
        y = route[x][1] + 1
        l_word = sentence[x:y]
        if re_eng.match(l_word) and len(l_word) == 1:
            buf += l_word
            x = y
        else:
            if buf:
                yield buf
                buf = u''
            yield l_word
            x = y
    if buf:
        yield buf
        buf = u''

def __cut_DAG(sentence):
    DAG = get_DAG(sentence)
    route = {}
    calc(sentence, DAG, route=route)
    x = 0
    buf = u''
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
                    buf = u''
                else:
                    if not in_FREQ(buf):
                        recognized = finalseg.cut(buf)
                        for t in recognized:
                            yield t
                    else:
                        for elem in buf:
                            yield elem
                    buf = u''
            yield l_word
        x = y

    if buf:
        if len(buf) == 1:
            yield buf
        elif not in_FREQ(buf):
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
        - sentence: The str/unicode to be segmented.
        - cut_all: Model type. True for full pattern, False for accurate pattern.
        - HMM: Whether to use the Hidden Markov Model.
    '''
    if not isinstance(sentence, unicode):
        try:
            sentence = sentence.decode('utf-8')
        except UnicodeDecodeError:
            sentence = sentence.decode('gbk', 'ignore')

    # \u4E00-\u9FA5a-zA-Z0-9+#&\._ : All non-space characters. Will be handled with re_han
    # \r\n|\s : whitespace characters. Will not be handled.

    if cut_all:
        re_han, re_skip = re.compile(ur"([\u4E00-\u9FA5]+)", re.U), re.compile(ur"[^a-zA-Z0-9+#\n]", re.U)
    else:
        re_han, re_skip = re.compile(ur"([\u4E00-\u9FA5a-zA-Z0-9+#&\._]+)", re.U), re.compile(ur"(\r\n|\s)", re.U)
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
            for i in xrange(len(w)-1):
                gram2 = w[i:i+2]
                if in_FREQ(gram2):
                    yield gram2
        if len(w) > 3:
            for i in xrange(len(w)-2):
                gram3 = w[i:i+3]
                if in_FREQ(gram3):
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
    if isinstance(f, (str, unicode)):
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
            word = word.replace(u'\ufeff',u"") #remove bom flag if it exists
        add_word(*tup)

@require_initialized
def add_word(word, freq, tag=None):
    global FREQ, pfdict, total, user_word_tag_tab, use_sqlite
    f = log(float(freq) / total)
    if not use_sqlite :
        FREQ[word] = f 
    else :
        use_sqlite["conn"].execute("insert into FREQ values (?, ?)", (word, f))

    if tag is not None:
        user_word_tag_tab[word] = tag.strip()
    for ch in xrange(len(word)):
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
    if sys.version_info[0]==2 and sys.version_info[1]<6:
        raise Exception("jieba: the parallel feature needs Python version>2.5")
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
        - sentence: the unicode to be segmented.
        - mode: "default" or "search", "search" is for finer segmentation.
        - HMM: whether to use the Hidden Markov Model.
    """
    if not isinstance(unicode_sentence, unicode):
        raise Exception("jieba: the input parameter should be unicode.")
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
                for i in xrange(len(w)-1):
                    gram2 = w[i:i+2]
                    if gram2 in FREQ:
                        yield (gram2, start+i, start+i+2)
            if len(w) > 3:
                for i in xrange(len(w)-2):
                    gram3 = w[i:i+3]
                    if gram3 in FREQ:
                        yield (gram3, start+i, start+i+3)
            yield (w, start, start+width)
            start += width
