# -*- coding: UTF-8 -*-
import jieba
#测试用例..............

def compare(str1):
    print('--------------------------------------------------------')
    print('-----cut_all-------')
    seg_list = jieba.cut(str1, cut_all=True, HMM=False,use_paddle=False)
    print(' '.join(list(seg_list)))
    print('-----use_paddle-------')
    seg_list = jieba.cut(str1, HMM=False,use_paddle=True)
    print(' '.join(list(seg_list)))
    print('-----not cut all-------')
    seg_list = jieba.cut(str1, cut_all=False, HMM=False,use_paddle=False)
    print(' '.join(list(seg_list)))
    print('-----use HMM-------')
    seg_list = jieba.cut(str1, cut_all=False, HMM=True,use_paddle=False)
    print(' '.join(list(seg_list)))
str1="我来到北京清华大学"
str2="乒乓球拍卖完了"
str3="中国科学技术大学"
str4="别把手放在我的肩膀上"
str5="质量和服务一样重要"
str6="他正在量和服尺寸"
str7="共同创造美好的新世纪——二〇〇一年新年贺词"
str8="雷猴回归人间。"
strs=["我来到北京清华大学","乒乓球拍卖完了","中国科学技术大学","别把手放在我的肩膀上","质量和服务一样重要","他正在量和服尺寸","共同创造美好的新世纪——二〇〇一年新年贺词","雷猴回归人间。","工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作。","隐马尔可夫","“Microsoft”一词由“MICROcomputer（微型计算机）”和“SOFTware（软件）”两部分组成","中国科学院计算技术研究所","罗密欧与朱丽叶","湖北省石首市","PS: 我觉得开源有一个好处，就是能够敦促自己不断改进，避免敞帚自珍","人们审美的观点是不同的。","外交部发言人马朝旭","AT&T是一件不错的公司，给你发offer了吗？","C++和c#是什么关系？11+122=133，是吗？","做好了这件事情就一了百了了","买水果然后来世博园","二〇〇一年十二月三十一日","张晓梅去人民医院做了个B超然后去买了件T恤","无线电法国别研究","过几天天天天气不好","骑车出门差点摔跤，还好我一把把把住了","来到儿子等校车的地方，邓超对孙俪说：“我也想等等等等等过的那辆车。","林俊杰做错了什么？为什么要绿他"]
for str1 in strs:
    compare(str1)

