# -*- coding: UTF-8 -*-
import sys
import os
sys.path.append("../")
from whoosh.index import create_in,open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser

from jieba.analyse import ChineseAnalyzer 

analyzer = ChineseAnalyzer()

schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True, analyzer=analyzer))
if not os.path.exists("tmp"):
    os.mkdir("tmp")
ix = open_dir("tmp")

searcher = ix.searcher()
parser = QueryParser("content", schema=ix.schema)

for keyword in (u"水果小姐",u"你",u"first",u"中文",u"交换机",u"交换",u"少林",u"乔峰"):
    print "result of ",keyword
    q = parser.parse(keyword)
    results = searcher.search(q)
    for hit in results:  
        print hit.highlights("content")
    print "="*10
