import sys,time
import sys
sys.path.append("../../")
import jieba

jieba.enable_parallel()

url = sys.argv[1]
with open(url,"rb") as content:
    content = content.read()
    t1 = time.time()
    words = "/ ".join(jieba.cut(content))
    t2 = time.time()
    tm_cost = t2-t1
    print('cost',tm_cost)
    print('speed' , len(content)/tm_cost, " bytes/second")

with open("1.log","wb") as log_f:
    log_f.write(words.encode('utf-8'))


