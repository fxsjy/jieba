#encoding=utf-8
import sys
sys.path.append("../")
import jieba
import jieba.posseg as pseg
words=pseg.cut("又跛又啞")
for w in words:
	print w.word,w.flag

