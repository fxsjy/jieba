# -*- coding: UTF-8 -*-
import sys,os
sys.path.append("../")
from whoosh.index import create_in,open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser

from jieba.analyse import ChineseAnalyzer

analyzer = ChineseAnalyzer()

schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True, analyzer=analyzer))
if not os.path.exists("tmp"):
    os.mkdir("tmp")

ix = create_in("tmp", schema) # for create new index
#ix = open_dir("tmp") # for read only
writer = ix.writer()

writer.add_document(
    title=u"document1",
    path=u"/a",
    content=u"This is the first document we’ve added!"
)

writer.add_document(
    title=u"document2",
    path=u"/b",
    content=u"The second one 你 中文测试中文 is even more interesting! 吃水果"
)

writer.add_document(
    title=u"document3",
    path=u"/c",
    content=u"买水果然后来世博园。"
)

writer.add_document(
    title=u"document4",
    path=u"/c",
    content=u"工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作"
)

writer.add_document(
    title=u"document4",
    path=u"/c",
    content=u"咱俩交换一下吧。"
)

writer.commit()
searcher = ix.searcher()
parser = QueryParser("content", schema=ix.schema)

for keyword in (u"水果世博园",u"你",u"first",u"中文",u"交换机",u"交换"):
    print "result of ",keyword
    q = parser.parse(keyword)
    results = searcher.search(q)
    for hit in results:
        print hit.highlights("content")
    print "="*10

for t in analyzer(u"我的好朋友是李明;我爱北京天安门;IBM和Microsoft; I have a dream. this is intetesting and interested me a lot"):
    print t.text
