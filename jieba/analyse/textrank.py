#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import sys
import collections
from operator import itemgetter
import jieba.posseg as pseg
from .._compat import *


class UndirectWeightedGraph:
    d = 0.85

    def __init__(self):
        self.graph = collections.defaultdict(list)

    def addEdge(self, start, end, weight):
        # use a tuple (start, end, weight) instead of a Edge object
        self.graph[start].append((start, end, weight))
        self.graph[end].append((end, start, weight))

    def rank(self):
        ws = collections.defaultdict(float)
        outSum = collections.defaultdict(float)

        wsdef = 1.0 / (len(self.graph) or 1.0)
        for n, out in self.graph.items():
            ws[n] = wsdef
            outSum[n] = sum((e[2] for e in out), 0.0)

        # this line for build stable iteration
        sorted_keys = sorted(self.graph.keys())
        for x in xrange(10):  # 10 iters
            for n in sorted_keys:
                s = 0
                for e in self.graph[n]:
                    s += e[2] / outSum[e[1]] * ws[e[1]]
                ws[n] = (1 - self.d) + self.d * s

        (min_rank, max_rank) = (sys.float_info[0], sys.float_info[3])

        for w in itervalues(ws):
            if w < min_rank:
                min_rank = w
            elif w > max_rank:
                max_rank = w

        for n, w in ws.items():
            # to unify the weights, don't *100.
            ws[n] = (w - min_rank / 10.0) / (max_rank - min_rank / 10.0)

        return ws


def textrank(sentence, topK=10, withWeight=False, allowPOS=['ns', 'n', 'vn', 'v']):
    """
    Extract keywords from sentence using TextRank algorithm.
    Parameter:
        - topK: return how many top keywords. `None` for all possible words.
        - withWeight: if True, return a list of (word, weight);
                      if False, return a list of words.
        - allowPOS: the allowed POS list eg. ['ns', 'n', 'vn', 'v'].
                    if the POS of w is not in this list,it will be filtered.
    """
    pos_filt = frozenset(allowPOS)
    g = UndirectWeightedGraph()
    cm = collections.defaultdict(int)
    span = 5
    words = list(pseg.cut(sentence))
    for i in xrange(len(words)):
        if words[i].flag in pos_filt:
            for j in xrange(i + 1, i + span):
                if j >= len(words):
                    break
                if words[j].flag not in pos_filt:
                    continue
                cm[(words[i].word, words[j].word)] += 1

    for terms, w in cm.items():
        g.addEdge(terms[0], terms[1], w)
    nodes_rank = g.rank()
    if withWeight:
        tags = sorted(nodes_rank.items(), key=itemgetter(1), reverse=True)
    else:
        tags = sorted(nodes_rank, key=nodes_rank.__getitem__, reverse=True)
    if topK:
        return tags[:topK]
    else:
        return tags

if __name__ == '__main__':
    s = "此外，公司拟对全资子公司吉林欧亚置业有限公司增资4.3亿元，增资后，吉林欧亚置业注册资本由7000万元增加到5亿元。吉林欧亚置业主要经营范围为房地产开发及百货零售等业务。目前在建吉林欧亚城市商业综合体项目。2013年，实现营业收入0万元，实现净利润-139.13万元。"
    for x, w in textrank(s, withWeight=True):
        print('%s %s' % (x, w))
