import urllib2
import sys,time
import sys
sys.path.append("../../")
import jieba

jieba.enable_parallel()

url = sys.argv[1]
content = open(url,"rb").read()
t1 = time.time()
words = "/ ".join(jieba.cut(content))

t2 = time.time()
tm_cost = t2-t1

log_f = open("1.log","wb")
log_f.write(words.encode('utf-8'))

print 'speed' , len(content)/tm_cost, " bytes/second"

