#encoding=utf-8
import sys
sys.path.append("../")

import jieba

seg_list = jieba.cut(u"我来到北京清华大学", cut_all=True)
print u"Full Mode:", u"/ ".join(seg_list)  # 全模式

seg_list = jieba.cut(u"我来到北京清华大学", cut_all=False)
print u"Default Mode:", u"/ ".join(seg_list)  # 默认模式

seg_list = jieba.cut(u"他来到了网易杭研大厦")
print u", ".join(seg_list)

seg_list = jieba.cut_for_search(u"小明硕士毕业于中国科学院计算所，后在日本京都大学深造")  # 搜索引擎模式
print u", ".join(seg_list)
