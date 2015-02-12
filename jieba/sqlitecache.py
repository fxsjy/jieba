# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from ._compat import *

available = False
try:
    import sqlite3
    available = True
except ImportError:
    pass


class SQLiteCacheDict:

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

    def addword(self, key, value):
        self.conn.execute('REPLACE INTO wordlist (word, freq) VALUES (?,?)',
                          (key, value))
        for ch in xrange(len(key)):
            self.conn.execute(
                "INSERT OR IGNORE INTO wordlist values (?, 0)",
                (key[:ch + 1],))

    def get(self, key, default=None):
        item = self.conn.execute('SELECT freq FROM wordlist WHERE word = ?',
                                 (key,)).fetchone()
        if item is None:
            return default
        else:
            return item[0]

    def execute(self, sql, parameters=None):
        return self.conn.execute(sql, parameters)


def gen_cachedb(f_name, cache_file):
    try:
        lfreq = SQLiteCacheDict(cache_file)
    except Exception:
        os.unlink(cache_file)
        lfreq = SQLiteCacheDict(cache_file)
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
