#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jieba.posseg as pseg
import collections
import sys


class Edge:

    def __init__(self, start, end, weight):
        self.start = start
        self.end = end
        self.weight = weight


class UndirectWeightedGraph:
    d = 0.85

    def __init__(self):
        self.graph = collections.defaultdict(list)

    def addEdge(self, start, end, weight):
        e1 = Edge(start, end, weight)
        e2 = Edge(end, start, weight)
        self.graph[start].append(e1)
        self.graph[end].append(e2)

    def rank(self):
        ws = collections.defaultdict(float)
        outSum = collections.defaultdict(float)

        for n, _ in self.graph.items():
            ws[n] = 1.0 / len(self.graph)

        for n, out in self.graph.items():
            os = 0.0
            for e in out:
                os += e.weight
            outSum[n] = os

        for x in xrange(10):  # 10 iters
            for n, inedges in self.graph.items():
                s = 0
                for e in inedges:
                    s += e.weight / outSum[e.end] * ws[e.end]
                ws[n] = (1 - self.d) + self.d * s

        (min_rank, max_rank) = (sys.float_info[0], sys.float_info[3])

        for _, w in ws.items():
            if w < min_rank:
                min_rank = w
            if w > max_rank:
                max_rank = w

        for n, w in ws.items():
            ws[n] = (w - min_rank / 10.0) / (max_rank - min_rank / 10.0) * 100

        return ws


def textrank(raw=None, topk=10):
    pos_filt = set(['ns', 'n', 'vn', 'v'])
    g = UndirectWeightedGraph()
    cm = collections.defaultdict(int)
    span = 5
    words = [x for x in pseg.cut(raw)]
    for i in xrange(len(words)):
        for j in xrange(i + 1, i + span):
            if j >= len(words):
                break
            if words[i].flag not in pos_filt or words[j].flag not in pos_filt:
                continue
            cm['%s:%s' % (words[i].word, words[j].word)] += 1

    for pair, w in cm.items():
        terms = pair.split(':')
        g.addEdge(terms[0], terms[1], w)

    nodes_rank = g.rank()
    nrs = sorted(nodes_rank.items(), key=lambda x: x[1], reverse=True)
    return nrs[:topk]

if __name__ == '__main__':
    for x, w in textrank("此外，公司拟对全资子公司吉林欧亚置业有限公司增资4.3亿元，增资后，吉林欧亚置业注册资本由7000万元增加到5亿元。吉林欧亚置业主要经营范围为房地产开发及百货零售等业务。目前在建吉林欧亚城市商业综合体项目。2013年，实现营业收入0万元，实现净利润-139.13万元。"):
        print x, w
