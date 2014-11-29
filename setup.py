# -*- coding: utf-8 -*-
from distutils.core import setup
LONGDOC = u"""
jieba
=====

“结巴”中文分词：做最好的 Python 中文分词组件

"Jieba" (Chinese for "to stutter") Chinese text segmentation: built to
be the best Python Chinese word segmentation module.

完整文档见 ``README.md``

GitHub: https://github.com/fxsjy/jieba

特点
====

-  支持三种分词模式：

   -  精确模式，试图将句子最精确地切开，适合文本分析；
   -  全模式，把句子中所有的可以成词的词语都扫描出来,
      速度非常快，但是不能解决歧义；
   -  搜索引擎模式，在精确模式的基础上，对长词再次切分，提高召回率，适合用于搜索引擎分词。

-  支持繁体分词
-  支持自定义词典

在线演示： http://jiebademo.ap01.aws.af.cm/

安装说明
========

Python 2.x
----------

-  全自动安装： ``easy_install jieba`` 或者 ``pip install jieba``
-  半自动安装：先下载 https://pypi.python.org/pypi/jieba/ ，解压后运行
   python setup.py install
-  手动安装：将 jieba 目录放置于当前目录或者 site-packages 目录
-  通过 ``import jieba`` 来引用

Python 3.x
----------

见 https://pypi.python.org/pypi/jieba3k/

-  目前 master 分支是只支持 Python 2.x 的
-  Python 3.x 版本的分支也已经基本可用：
   https://github.com/fxsjy/jieba/tree/jieba3k

.. code:: bash

    git clone https://github.com/fxsjy/jieba.git
    git checkout jieba3k
    python setup.py install

-  或使用pip3安装： pip3 install jieba3k

"""

setup(name='jieba',
      version='0.35',
      description='Chinese Words Segementation Utilities',
      long_description=LONGDOC,
      author='Sun, Junyi',
      author_email='ccnusjy@gmail.com',
      url='https://github.com/fxsjy/jieba',
      license="MIT",
      classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='NLP,tokenizing,Chinese word segementation',
      packages=['jieba'],
      package_dir={'jieba':'jieba'},
      package_data={'jieba':['*.*','finalseg/*','analyse/*','posseg/*']}
)
