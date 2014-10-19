#encoding=utf-8
import sys
sys.path.append("../")
import jieba
jieba.load_userdict("userdict.txt")
import jieba.posseg as pseg

test_sent = "李小福是创新办主任也是云计算方面的专家; 什么是八一双鹿"
test_sent += "例如我输入一个带“韩玉赏鉴”的标题，在自定义词库中也增加了此词为N类型"
words = jieba.cut(test_sent)
for w in words:
    print w

result = pseg.cut(test_sent)

for w in result:
    print w.word, "/", w.flag, ", ",

print "\n========"

terms = jieba.cut('easy_install is great')
for t in terms:
    print t
print '-------------------------'
terms = jieba.cut('python 的正则表达式是好用的')
for t in terms:
    print t
