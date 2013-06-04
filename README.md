jieba
========
"结巴"中文分词：做最好的Python中文分词组件
"Jieba" (Chinese for "to stutter") Chinese text segmentation: built to be the best Python Chinese word segmentation module.
- _Scroll down for English documentation._

Feature
========
* 支持三种分词模式：
	* 精确模式，试图将句子最精确地切开，适合文本分析；
	* 全模式，把句子中所有的可以成词的词语都扫描出来, 速度非常快，但是不能解决歧义；
	* 搜索引擎模式，在精确模式的基础上，对长词再次切分，提高召回率，适合用于搜索引擎分词。

* 支持繁体分词
* 支持自定义词典


在线演示
=========
http://jiebademo.ap01.aws.af.cm/

(Powered by Appfog)


Python 2.x 下的安装
===================
* 全自动安装：`easy_install jieba` 或者 `pip install jieba`
* 半自动安装：先下载http://pypi.python.org/pypi/jieba/ ，解压后运行python setup.py install
* 手动安装：将jieba目录放置于当前目录或者site-packages目录
* 通过import jieba 来引用


Python 3.x 下的安装
====================
* 目前master分支是只支持Python2.x 的
* Python3.x 版本的分支也已经基本可用： https://github.com/fxsjy/jieba/tree/jieba3k

        git clone https://github.com/fxsjy/jieba.git
        git checkout jieba3k
        python setup.py install


Algorithm
========
* 基于Trie树结构实现高效的词图扫描，生成句子中汉字所有可能成词情况所构成的有向无环图（DAG)
* 采用了动态规划查找最大概率路径, 找出基于词频的最大切分组合
* 对于未登录词，采用了基于汉字成词能力的HMM模型，使用了Viterbi算法

功能 1)：分词
==========
* `jieba.cut`方法接受两个输入参数: 1) 第一个参数为需要分词的字符串 2）cut_all参数用来控制是否采用全模式
* `jieba.cut_for_search`方法接受一个参数：需要分词的字符串,该方法适合用于搜索引擎构建倒排索引的分词，粒度比较细
* 注意：待分词的字符串可以是gbk字符串、utf-8字符串或者unicode
* `jieba.cut`以及`jieba.cut_for_search`返回的结构都是一个可迭代的generator，可以使用for循环来获得分词后得到的每一个词语(unicode)，也可以用list(jieba.cut(...))转化为list

代码示例( 分词 )

	#encoding=utf-8
	import jieba

	seg_list = jieba.cut("我来到北京清华大学", cut_all=True)
	print "Full Mode:", "/ ".join(seg_list)  # 全模式

	seg_list = jieba.cut("我来到北京清华大学", cut_all=False)
	print "Default Mode:", "/ ".join(seg_list)  # 精确模式

	seg_list = jieba.cut("他来到了网易杭研大厦")  # 默认是精确模式
	print ", ".join(seg_list)

	seg_list = jieba.cut_for_search("小明硕士毕业于中国科学院计算所，后在日本京都大学深造")  # 搜索引擎模式
	print ", ".join(seg_list)

Output:

	【全模式】: 我/ 来到/ 北京/ 清华/ 清华大学/ 华大/ 大学

	【精确模式】: 我/ 来到/ 北京/ 清华大学

	【新词识别】：他, 来到, 了, 网易, 杭研, 大厦    (此处，“杭研”并没有在词典中，但是也被Viterbi算法识别出来了)

	【搜索引擎模式】： 小明, 硕士, 毕业, 于, 中国, 科学, 学院, 科学院, 中国科学院, 计算, 计算所, 后, 在, 日本, 京都, 大学, 日本京都大学, 深造

功能 2) ：添加自定义词典
================

* 开发者可以指定自己自定义的词典，以便包含jieba词库里没有的词。虽然jieba有新词识别能力，但是自行添加新词可以保证更高的正确率
* 用法： jieba.load_userdict(file_name) # file_name为自定义词典的路径
* 词典格式和`dict.txt`一样，一个词占一行；每一行分三部分，一部分为词语，另一部分为词频，最后为词性（可省略），用空格隔开
* 范例：

	* 自定义词典：https://github.com/fxsjy/jieba/blob/master/test/userdict.txt
	
	* 用法示例：https://github.com/fxsjy/jieba/blob/master/test/test_userdict.py
	

		* 之前： 李小福 / 是 / 创新 / 办 / 主任 / 也 / 是 / 云 / 计算 / 方面 / 的 / 专家 /

		* 加载自定义词库后：　李小福 / 是 / 创新办 / 主任 / 也 / 是 / 云计算 / 方面 / 的 / 专家 /

		
* "通过用户自定义词典来增强歧义纠错能力" --- https://github.com/fxsjy/jieba/issues/14

功能 3) ：关键词提取
================
* jieba.analyse.extract_tags(sentence,topK) #需要先import jieba.analyse
* setence为待提取的文本
* topK为返回几个TF/IDF权重最大的关键词，默认值为20

代码示例 （关键词提取）

	https://github.com/fxsjy/jieba/blob/master/test/extract_tags.py

功能 4) : 词性标注
================
* 标注句子分词后每个词的词性，采用和ictclas兼容的标记法
* 用法示例

		>>> import jieba.posseg as pseg
		>>> words = pseg.cut("我爱北京天安门")
		>>> for w in words:
		...    print w.word, w.flag
		...
		我 r
		爱 v
		北京 ns
		天安门 ns
		
功能 5) : 并行分词
==================
* 原理：将目标文本按行分隔后，把各行文本分配到多个python进程并行分词，然后归并结果，从而获得分词速度的可观提升
* 基于python自带的multiprocessing模块，目前暂不支持windows
* 用法：
	* `jieba.enable_parallel(4)` # 开启并行分词模式，参数为并行进程数
	* `jieba.disable_parallel()` # 关闭并行分词模式

* 例子：
		https://github.com/fxsjy/jieba/blob/master/test/parallel/test_file.py

* 实验结果：在4核3.4GHz Linux机器上，对金庸全集进行精确分词，获得了1MB/s的速度，是单进程版的3.3倍。

其他词典
========
1. 占用内存较小的词典文件
https://github.com/fxsjy/jieba/raw/master/extra_dict/dict.txt.small

2. 支持繁体分词更好的词典文件
https://github.com/fxsjy/jieba/raw/master/extra_dict/dict.txt.big

下载你所需要的词典，然后覆盖jieba/dict.txt 即可或者用`jieba.set_dictionary('data/dict.txt.big')`


模块初始化机制的改变:lazy load （从0.28版本开始）
================================================

jieba采用延迟加载，"import jieba"不会立即触发词典的加载，一旦有必要才开始加载词典构建trie。如果你想手工初始jieba，也可以手动初始化。

    import jieba
    jieba.initialize()  # 手动初始化（可选）


在0.28之前的版本是不能指定主词典的路径的，有了延迟加载机制后，你可以改变主词典的路径:


    jieba.set_dictionary('data/dict.txt.big')


例子： https://github.com/fxsjy/jieba/blob/master/test/test_change_dictpath.py



分词速度
=========
* 1.5 MB / Second in Full Mode
* 400 KB / Second in Default Mode
* Test Env: Intel(R) Core(TM) i7-2600 CPU @ 3.4GHz；《围城》.txt


常见问题
=========
 1）模型的数据是如何生成的？https://github.com/fxsjy/jieba/issues/7
 
 2）这个库的授权是? https://github.com/fxsjy/jieba/issues/2
 
 更多问题请点击：https://github.com/fxsjy/jieba/issues?sort=updated&state=closed
 
Change Log
==========
https://github.com/fxsjy/jieba/blob/master/Changelog

jieba
========
"Jieba" (Chinese for "to stutter") Chinese text segmentation: built to be the best Python Chinese word segmentation module.

Features
========
* Support three types of segmentation mode:
* 1) Accurate Mode, attempt to cut the sentence into the most accurate segmentation, which is suitable for text analysis;
* 2) Full Mode, break the words of the sentence into words scanned
* 3) Search Engine Mode, based on the Accurate Mode, with an attempt to cut the long words into several short words, which can enhance the recall rate

Usage
========
* Fully automatic installation: `easy_install jieba` or `pip install jieba`
* Semi-automatic installation: Download http://pypi.python.org/pypi/jieba/ , after extracting run `python setup.py install`
* Manutal installation: place the `jieba` directory in the current directory or python site-packages directory.
* Use `import jieba` to import, which will first build the Trie tree only on first import (takes a few seconds).

Algorithm
========
* Based on the Trie tree structure to achieve efficient word graph scanning; sentences using Chinese characters constitute a directed acyclic graph (DAG)
* Employs memory search to calculate the maximum probability path, in order to identify the maximum tangential points based on word frequency combination
* For unknown words, the character position HMM-based model is used, using the Viterbi algorithm

Function 1): cut
==========
* The `jieba.cut` method accepts to input parameters: 1) the first parameter is the string that requires segmentation, and the 2) second parameter is `cut_all`, a parameter used to control the segmentation pattern.
* `jieba.cut` returned structure is an iterative generator, where you can use a `for` loop to get the word segmentation (in unicode), or `list(jieba.cut( ... ))` to create a list.
* `jieba.cut_for_search` accpets only on parameter: the string that requires segmentation, and it will cut the sentence into short words

Code example: segmentation
==========

	#encoding=utf-8
	import jieba

	seg_list = jieba.cut("我来到北京清华大学", cut_all=True)
	print "Full Mode:", "/ ".join(seg_list)  # 全模式

	seg_list = jieba.cut("我来到北京清华大学", cut_all=False)
	print "Default Mode:", "/ ".join(seg_list)  # 默认模式

	seg_list = jieba.cut("他来到了网易杭研大厦")
	print ", ".join(seg_list)

	seg_list = jieba.cut_for_search("小明硕士毕业于中国科学院计算所，后在日本京都大学深造")  # 搜索引擎模式
	print ", ".join(seg_list)

Output:

	[Full Mode]: 我/ 来到/ 北京/ 清华/ 清华大学/ 华大/ 大学

	[Accurate Mode]: 我/ 来到/ 北京/ 清华大学

	[Unknown Words Recognize] 他, 来到, 了, 网易, 杭研, 大厦    (In this case, "杭研" is not in the dictionary, but is identified by the Viterbi algorithm)

	[Search Engine Mode]： 小明, 硕士, 毕业, 于, 中国, 科学, 学院, 科学院, 中国科学院, 计算, 计算所, 后, 在
, 日本, 京都, 大学, 日本京都大学, 深造


Function 2): Add a custom dictionary
==========

* Developers can specify their own custom dictionary to include in the jieba thesaurus. jieba has the ability to identify new words, but adding your own new words can ensure a higher rate of correct segmentation.
* Usage： `jieba.load_userdict(file_name) # file_name is a custom dictionary path`
* The dictionary format is the same as that of `analyse/idf.txt`: one word per line; each line is divided into two parts, the first is the word itself, the other is the word frequency, separated by a space
* Example：

		云计算 5
		李小福 2
		创新办 3

		之前： 李小福 / 是 / 创新 / 办 / 主任 / 也 / 是 / 云 / 计算 / 方面 / 的 / 专家 /

		加载自定义词库后：　李小福 / 是 / 创新办 / 主任 / 也 / 是 / 云计算 / 方面 / 的 / 专家 /

Function 3): Keyword Extraction
================
* `jieba.analyse.extract_tags(sentence,topK) # needs to first import jieba.analyse`
* `setence`: the text to be extracted
* `topK`: To return several TF / IDF weights for the biggest keywords, the default value is 20

Code sample (keyword extraction)

	https://github.com/fxsjy/jieba/blob/master/test/extract_tags.py

Using Other Dictionaries
========
It is possible to supply Jieba with your own custom dictionary, and there are also two dictionaries readily available for download:

1. You can employ a smaller dictionary for a smaller memory footprint:
https://github.com/fxsjy/jieba/raw/master/extra_dict/dict.txt.small

2. There is also a bigger file that has better support for traditional characters (繁體):
https://github.com/fxsjy/jieba/raw/master/extra_dict/dict.txt.big

By default, an in-between dictionary is used, called `dict.txt` and included in the distribution.

In either case, download the file you want first, and then call `jieba.set_dictionary('data/dict.txt.big')` or just replace the existing `dict.txt`.

Initialization
========
By default, Jieba employs lazy loading to only build the trie once it is necessary. This takes 1-3 seconds once, after which it is not initialized again. If you want to initialize Jieba manually, you can call:

    import jieba
    jieba.initialize()  # (optional)

You can also specify the dictionary (not supported before version 0.28) :
    
    jieba.set_dictionary('data/dict.txt.big')

Segmentation speed
=========
* 1.5 MB / Second in Full Mode
* 400 KB / Second in Default Mode
* Test Env: Intel(R) Core(TM) i7-2600 CPU @ 3.4GHz；《围城》.txt

Online demo
=========
http://jiebademo.ap01.aws.af.cm/

(Powered by Appfog)
