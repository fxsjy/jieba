jieba
========
"结巴"中文分词：做最好的Python中文分词组件
"Jieba" (Chinese for "to stutter") Chinese text segmentation: built to be the best Python Chinese word segmentation module.
- _Scroll down for English documentation._

Feature
========
* 支持两种分词模式：
* 1）默认模式，试图将句子最精确地切开，适合文本分析；
* 2）全模式，把句子中所有的可以成词的词语都扫描出来，适合搜索引擎。

Usage
========
* 全自动安装：`easy_install jieba` 或者 `pip install jieba`
* 半自动安装：先下载http://pypi.python.org/pypi/jieba/ ，解压后运行python setup.py install
* 手动安装：将jieba目录放置于当前目录或者site-packages目录
* 通过import jieba 来引用 （第一次import时需要构建Trie树，需要几秒时间）

Algorithm
========
* 基于Trie树结构实现高效的词图扫描，生成句子中汉字所有可能成词情况所构成的有向无环图（DAG)
* 采用了动态规划查找最大概率路径, 找出基于词频的最大切分组合
* 对于未登录词，采用了基于汉字成词能力的HMM模型，使用了Viterbi算法

功能 1)：分词
==========
* jieba.cut方法接受两个输入参数: 1) 第一个参数为需要分词的字符串 2）cut_all参数用来控制分词模式
* 待分词的字符串可以是gbk字符串、utf-8字符串或者unicode
* jieba.cut返回的结构是一个可迭代的generator，可以使用for循环来获得分词后得到的每一个词语(unicode)，也可以用list(jieba.cut(...))转化为list

代码示例( 分词 )

	#encoding=utf-8
	import jieba

	seg_list = jieba.cut("我来到北京清华大学",cut_all=True)
	print "Full Mode:", "/ ".join(seg_list) #全模式

	seg_list = jieba.cut("我来到北京清华大学",cut_all=False)
	print "Default Mode:", "/ ".join(seg_list) #默认模式

	seg_list = jieba.cut("他来到了网易杭研大厦")
	print ", ".join(seg_list)

Output:

	Full Mode: 我/ 来到/ 北京/ 清华/ 清华大学/ 华大/ 大学

	Default Mode: 我/ 来到/ 北京/ 清华大学

	他, 来到, 了, 网易, 杭研, 大厦    (此处，“杭研”并没有在词典中，但是也被Viterbi算法识别出来了)

功能 2) ：添加自定义词典
================

* 开发者可以指定自己自定义的词典，以便包含jieba词库里没有的词。虽然jieba有新词识别能力，但是自行添加新词可以保证更高的正确率
* 用法： jieba.load_userdict(file_name) # file_name为自定义词典的路径
* 词典格式和`analyse/idf.txt`一样，一个词占一行；每一行分为两部分，一部分为词语，另一部分为词频，用空格隔开
* 范例：

		云计算 5
		李小福 2
		创新办 3

		之前： 李小福 / 是 / 创新 / 办 / 主任 / 也 / 是 / 云 / 计算 / 方面 / 的 / 专家 /

		加载自定义词库后：　李小福 / 是 / 创新办 / 主任 / 也 / 是 / 云计算 / 方面 / 的 / 专家 /
		
* 通过用户自定义词典来增强歧义纠错能力： https://github.com/fxsjy/jieba/issues/14

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
		>>> words =pseg.cut("我爱北京天安门")
		>>> for w in words:
		...    print w.word,w.flag
		...
		我 r
		爱 v
		北京 ns
		天安门 ns



分词速度
=========
* 1.5 MB / Second in Full Mode
* 400 KB / Second in Default Mode
* Test Env: Intel(R) Core(TM) i7-2600 CPU @ 3.4GHz；《围城》.txt

在线演示
=========
http://209.222.69.242:9000/

常见问题
=========
 1）模型的数据是如何生成的？https://github.com/fxsjy/jieba/issues/7
 2）这个库的授权是? https://github.com/fxsjy/jieba/issues/2


jieba
========
"Jieba" (Chinese for "to stutter") Chinese text segmentation: built to be the best Python Chinese word segmentation module.

Features
========
* Support two types of segmentation mode:
* 1) Default mode, attempt to cut the sentence into the most accurate segmentation, which is suitable for text analysis;
* 2) Full mode, break the words of the sentence into words scanned, which is suitable for search engines.

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
* For unknown words, the character position probability-based model is used, using the Viterbi algorithm

Function 1): cut
==========
* The `jieba.cut` method accepts to input parameters: 1) the first parameter is the string that requires segmentation, and the 2) second parameter is `cut_all`, a parameter used to control the segmentation pattern.
* `jieba.cut` returned structure is an iterative generator, where you can use a `for` loop to get the word segmentation (in unicode), or `list(jieba.cut( ... ))` to create a list.

Code example: segmentation
==========

	#encoding=utf-8
	import jieba

	seg_list = jieba.cut("我来到北京清华大学",cut_all=True)
	print "Full Mode:", "/ ".join(seg_list) #全模式

	seg_list = jieba.cut("我来到北京清华大学",cut_all=False)
	print "Default Mode:", "/ ".join(seg_list) #默认模式

	seg_list = jieba.cut("他来到了网易杭研大厦")
	print ", ".join(seg_list)


Output:

	Full Mode: 我/ 来到/ 北京/ 清华/ 清华大学/ 华大/ 大学

	Default Mode: 我/ 来到/ 北京/ 清华大学

	他, 来到, 了, 网易, 杭研, 大厦    (In this case, "杭研" is not in the dictionary, but is identified by the Viterbi algorithm)

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


Segmentation speed
=========
* 1.5 MB / Second in Full Mode
* 400 KB / Second in Default Mode
* Test Env: Intel(R) Core(TM) i7-2600 CPU @ 3.4GHz；《围城》.txt

Online demo
=========
http://209.222.69.242:9000/
