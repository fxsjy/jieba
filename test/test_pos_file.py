from __future__ import print_function
import sys
import time
sys.path.append("../")
import jieba
jieba.initialize()
import jieba.posseg as pseg

url = sys.argv[1]
content = open(url,"rb").read()
t1 = time.time()
words = list(pseg.cut(content))

t2 = time.time()
tm_cost = t2-t1

log_f = open("1.log","w")
log_f.write(' / '.join(map(str, words)))

print('speed' , len(content)/tm_cost, " bytes/second")

