import sys,time
import sys
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

log_f = open("1.log","wb")
for w in words:
    log_f.write(bytes(w.word+"/"+w.flag+" ",'utf-8'))

print('speed' , len(content)/tm_cost, " bytes/second")

