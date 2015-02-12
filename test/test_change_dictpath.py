#encoding=utf-8
from __future__ import print_function
import sys
sys.path.append("../")
import jieba

def cuttest(test_sent):
    result = jieba.cut(test_sent)
    print("  ".join(result))

def testcase():
    cuttest("这是一个伸手不见五指的黑夜。我叫孙悟空，我爱北京，我爱Python和C++。")
    cuttest("我不喜欢日本和服。")
    cuttest("雷猴回归人间。")
    cuttest("工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作")
    cuttest("我需要廉租房")
    cuttest("永和服装饰品有限公司")
    cuttest("我爱北京天安门")
    cuttest("abc")
    cuttest("隐马尔可夫")
    cuttest("雷猴是个好网站")
    
if __name__ == "__main__":
    testcase()
    jieba.set_dictionary("foobar.txt")
    print("================================")
    testcase()

