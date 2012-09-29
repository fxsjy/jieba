jieba
========
结巴中文分词：像结巴说话一样把所有词都分出来

Usage
========
* 将jieba目录放置于当前目录或者site-packages目录



代码示例

	#encoding=utf-8
	import jieba

	seg_list = jieba.cut("我爱北京天安门")
	print "/ ".join(seg_list)

Output:
	* 我/ 爱/ 北/ 北京/ 天/ 天安/ 天安门/ 门

Performance
=========
* 1.5 MB / Second
* Test Env: Intel(R) Core(TM) i7-2600 CPU @ 3.4GHz；《围城》.txt

Example
=========
* 在线分词效果展示  https://jiebademo.appspot.com/   (需要翻墙)
