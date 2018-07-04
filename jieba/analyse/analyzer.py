# encoding=utf-8
from __future__ import unicode_literals
from whoosh.analysis import RegexAnalyzer, LowercaseFilter, StopFilter, StemFilter
from whoosh.analysis import Tokenizer, Token
from whoosh.lang.porter import stem

import jieba
import re

STOP_WORDS = frozenset(('a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'can',
                        'for', 'from', 'have', 'if', 'in', 'is', 'it', 'may',
                        'not', 'of', 'on', 'or', 'tbd', 'that', 'the', 'this',
                        'to', 'us', 'we', 'when', 'will', 'with', 'yet',
                        'you', 'your', '的', '了', '和'))

accepted_chars = re.compile(r"[\u4E00-\u9FD5]+")


class ChineseTokenizer(Tokenizer):

    def __init__(self, mode, cut_all, **kargs):
        self.mode = mode
        self.cut_all = cut_all

    def __call__(self, text, **kargs):
        words = jieba.tokenize(text, mode=self.mode, cut_all=self.cut_all)
        token = Token()
        for (w, start_pos, stop_pos) in words:
            if not accepted_chars.match(w) and len(w) <= 1:
                continue
            token.original = token.text = w
            token.pos = start_pos
            token.startchar = start_pos
            token.endchar = stop_pos
            yield token


def ChineseAnalyzer(stoplist=STOP_WORDS, minsize=1, stemfn=stem, cachesize=50000, mode="search", cut_all=False):
    return (ChineseTokenizer(mode=mode, cut_all=cut_all) | LowercaseFilter() |
            StopFilter(stoplist=stoplist, minsize=minsize) |
            StemFilter(stemfn=stemfn, ignore=None, cachesize=cachesize))
