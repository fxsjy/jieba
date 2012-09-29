#encoding=utf-8
import sys
import jieba

def cuttest(test_sent):
	result = jieba.cut(test_sent)
	for word in result:
		print word, "/", 
	print ""


if __name__ == "__main__":
	cuttest("工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作")
	cuttest("永和服装饰品有限公司")
	cuttest("我爱北京天安门")