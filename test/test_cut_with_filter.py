#encoding=utf-8
from __future__ import print_function
import sys
sys.path.append("../")
import jieba

def cuttest(test_sent):
    result = jieba.cut_for_search(test_sent)
    for word in result:
        print(word, "/", end=' ')
    print('\n')
    jieba.set_stop_words('stop_word.txt')
    result = jieba.cut_with_filter(test_sent)
    for word in result:
        print(word, "/", end=' ')
    print("")


if __name__ == "__main__":
    cuttest("这是一个伸手不见五指的黑夜。我叫孙悟空，我爱北京，我爱Python和C++。")
    cuttest("我不喜欢日本和服。")
    cuttest("雷猴回归人间。")
    cuttest("工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作")    
