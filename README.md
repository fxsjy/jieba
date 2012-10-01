jieba
========
"结巴"中文分词：做最好的Python中文分词组件

Feature
========
* 支持两种分词模式：
* 1）默认模式，试图将句子最精确地切开，适合文本分析；
* 2）全模式，把句子中所有的可以成词的词语都扫描出来，适合搜索引擎。

Usage
========
* 自动安装：python setup.py install
* 手动安装：将jieba目录放置于当前目录或者site-packages目录
* 通过import jieba 来引用 （第一次import时需要构建Trie树，需要几秒时间）

Algorithm
========
* 基于Trie树结构实现高效的词图扫描，生成句子中汉字构成的有向无环图（DAG)
* 采用了记忆化搜索实现最大概率路径的计算, 找出基于词频的最大切分组合
* 对于未登录词，采用了基于汉字位置概率的模型，使用了Viterbi算法


代码示例

	#encoding=utf-8
	import jieba

	seg_list = jieba.cut("我来到北京清华大学",cut_all=True)
	print "Full Mode:", "/ ".join(seg_list) #全模式

	seg_list = jieba.cut("我来到北京清华大学",cut_all=False)
	print "Default Mode:", "/ ".join(seg_list) #默认模式

	seg_list = jieba.cut("他来到了网易杭研大厦")
	print ", ".join(seg_list)

Output:

	Full Mode: 我/ 来/ 来到/ 到/ 北/ 北京/ 京/ 清/ 清华/ 清华大学/ 华/ 华大/ 大/ 大学/ 学

	Default Mode: 我/ 来到/ 北京/ 清华大学

	他, 来到, 了, 网易, 杭研, 大厦    (此处，“杭研”并没有在词典中，但是也被Viterbi算法识别出来了)

Performance
=========
* 1.5 MB / Second in Full Mode
* 200 KB / Second in Default Mode
* Test Env: Intel(R) Core(TM) i7-2600 CPU @ 3.4GHz；《围城》.txt

