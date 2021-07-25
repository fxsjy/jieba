from __future__ import print_function
import sys,time
import sys
sys.path.append("../../")
import jieba
import jieba.posseg as pseg

jieba.enable_parallel(4)

url = sys.argv[1]
with open(url, 'rb') as f:
    content = f.read()
t1 = time.time()
words = list(pseg.cut(content))

t2 = time.time()
tm_cost = t2-t1

log_f = open("1.log","w")
log_f.write(' / '.join(map(str, words)))
log_f.close()

print('speed' , len(content)/tm_cost, " bytes/second")

