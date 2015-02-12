# -*- coding: utf-8 -*-
from __future__ import absolute_import
import collections
from ._compat import *

available = False
try:
    import sqlite3
    available = True
except ImportError:
    pass


class SQLiteCacheDict(collections.UserDict):

    def __init__(self, filename=None):
        self.db = sqlite3.connect(filename)
        self.conn = self.db.cursor()
        self.conn.execute('PRAGMA journal_mode=OFF')
        self.conn.execute('PRAGMA synchronous=OFF')
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS wordlist (word TEXT PRIMARY KEY, freq INTEGER)")

    def __contains__(self, key):
        return self.conn.execute('SELECT 1 FROM wordlist WHERE word = ?',
                                 (key,)).fetchone() is not None

    def __getitem__(self, key):
        item = self.conn.execute('SELECT freq FROM wordlist WHERE word = ?',
                                 (key,)).fetchone()
        if item is None:
            raise KeyError(key)
        return item[0]

    def __setitem__(self, key, value):
        self.conn.execute('REPLACE INTO wordlist (word, freq) VALUES (?,?)',
                          (key, value))

    def addword(self, key, value)
        self.conn.execute('REPLACE INTO wordlist (word, freq) VALUES (?,?)',
                          (key, value))
        for ch in xrange(len(key)):
            self.conn.execute(
                "INSERT OR IGNORE INTO wordlist values (?, 0)",
                (key[:ch + 1],))

    def get(self, key, default=None):
        item = self.conn.execute('SELECT freq FROM wordlist WHERE word = ?',
                                 (key,)).fetchone()
        if result is None:
            return default
        else:
            return result[0]

    def execute(self, sql, parameters=None):
        return self.conn.execute(sql, parameters)


def gen_cachedb(f_name):
    lfreq = SQLiteCacheDict()
    lfreq.db.isolation_level = None
    # Optimal sqlite memory cache size seems to be '30'
    # after doing a binary search between 1 and 2000
    lfreq.conn.execute('PRAGMA cache_size=30')
    lfreq.conn.execute("BEGIN")

    ltotal = 0
    with open(f_name, 'rb', 0) as f:
        lineno = 0
        while 1:
            line = f.readline()
            if not line:
                break
            line = line.rstrip().decode('utf-8')
            lineno += 1
            try:
                word, freq = line.split(' ')[:2]
                freq = int(freq)
                lfreq.addword(word, freq)
                ltotal += freq
            except ValueError as e:
                logger.debug('%s at line %s %s' % (f_name, lineno, line))
                raise e
    lfreq.conn.execute('REPLACE INTO wordlist (word, freq) VALUES (?,?)',
                       ("#TOTAL#", ltotal))
    lfreq.conn.execute("COMMIT")
    lfreq.conn.execute("VACUUM")
    lfreq.conn.execute('PRAGMA cache_size=2000')  # default
    return lfreq, ltotal


def get_DAG(sentence):
    global FREQ
    DAG = {}
    N = len(sentence)
    for k in xrange(N):
        tmplist = []
        i = k
        frag = sentence[k]
        while i < N:
            result = FREQ.get(frag)
            if result is None:
                break
            elif result:
                tmplist.append(i)
            i += 1
            frag = sentence[k:i + 1]
        if not tmplist:
            tmplist.append(k)
        DAG[k] = tmplist
    return DAG


def add_word(word, freq, tag=None):
    global FREQ, total, user_word_tag_tab
    freq = int(freq)
    FREQ.addword(word, freq)
    total += freq
    if tag is not None:
        user_word_tag_tab[word] = tag


def _______________():
    init_sqlite('/tmp/jieba.sqlcache')
    pfdict, FREQ, totala = gen_pfdict(
        '/home/gumble/github/jieba/jieba/dict.txt')
    a, FREQ1, totala = gen_pfidict('/home/gumble/github/jieba/jieba/dict.txt')
    a, b, totalb = gen_cache('/home/gumble/github/jieba/jieba/dict.txt')

    #assert totala == totalb

    total = totala
    merge = lambda dag: '\n'.join(
        ' '.join(s[i:j + 1] for j in dag[i]) for i in sorted(dag.keys()))

    dag1 = get_DAG(s)
    dag2 = get_DAGsql(s)
    dag3 = get_DAGi(s)
    print(merge(dag1))
    print(merge(dag2))
    print(merge(dag3))
    assert dag1 == dag2 == dag3

    st = time.clock()
    for i in range(20000):
        get_DAG(s)
    print("get_DAG(s) " + str(time.clock() - st))

    st = time.clock()
    for i in range(20000):
        get_DAGi(s)
    print("get_DAGi(s) " + str(time.clock() - st))

    st = time.clock()
    for i in range(20000):
        get_DAGi2(s)
    print("get_DAGi2(s) " + str(time.clock() - st))

    st = time.clock()
    for i in range(1000):
        get_DAGsql(s)
    print("get_DAGsql(s) " + str(time.clock() - st))
