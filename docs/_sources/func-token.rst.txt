功能简介
=========

分词
#####


不带词性的切分: 参见 :py:func:`jieba.cut`, :py:func:`jieba.lcut`
-----------------------------------------------------------------------

默认使用带HMM的精确模式,不使用paddle, 调用默认分词器 :py:meth:`jieba.Tokenizer.cut`
对序列进行不带词性的切分.

例子:


.. code-block:: python

    # encoding=utf-8
    import jieba

    jieba.enable_paddle()# 启动paddle模式。 0.40版之后开始支持，早期版本不支持
    strs=["我来到北京清华大学","乒乓球拍卖完了","中国科学技术大学"]
    for str in strs:
        seg_list = jieba.cut(str,use_paddle=True) # 使用paddle模式
        print("Paddle Mode: " + '/'.join(list(seg_list)))

    seg_list = jieba.cut("我来到北京清华大学", cut_all=True)
    print("Full Mode: " + "/ ".join(seg_list))  # 全模式

    seg_list = jieba.cut("我来到北京清华大学", cut_all=False)
    print("Default Mode: " + "/ ".join(seg_list))  # 精确模式

    seg_list = jieba.cut("他来到了网易杭研大厦")  # 默认是精确模式
    print(", ".join(seg_list))

    seg_list = jieba.cut_for_search("小明硕士毕业于中国科学院计算所，后在日本京都大学深造")  # 搜索引擎模式
    print(", ".join(seg_list))

结果:

.. code-block::

       【全模式】: 我/ 来到/ 北京/ 清华/ 清华大学/ 华大/ 大学

       【精确模式】: 我/ 来到/ 北京/ 清华大学

       【新词识别】：他, 来到, 了, 网易, 杭研, 大厦    (此处，“杭研”并没有在词典中，但是也被Viterbi算法识别出来了)

       【搜索引擎模式】： 小明, 硕士, 毕业, 于, 中国, 科学, 学院, 科学院, 中国科学院, 计算, 计算所, 后, 在, 日本, 京都, 大学, 日本京都大学, 深造


带词性的切分: 参见 :py:func:`jieba.posseg.cut`, :py:func:`jieba.posseg.lcut`
-------------------------------------------------------------------------


适合用于搜索引擎构建倒排索引的分词，粒度比较细 参见 :py:func:`jieba.cut_for_search`
-------------------------------------------------------------------------


新建自定义分词器，可用于同时使用不同词典。参见 :py:meth:`jieba.Tokenizer.__init__`
-------------------------------------------------------------------------

备注
------------

- :py:class:`sentence` :  待分词的字符串可以是 unicode 或 UTF-8 字符串、GBK 字符串。注意：不建议直接输入 GBK 字符串，可能无法预料地错误解码成 UTF-8
- :py:func:`jieba.lcut`  以及  :py:func:`jieba.lcut_for_search` 直接返回 list
