#encoding=utf-8
import jieba
import os
try:
    from analyzer import ChineseAnalyzer
except ImportError:
    pass
from textrank import textrank

_curpath = os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
abs_path = os.path.join(_curpath, "idf.txt")

STOP_WORDS = set((
    "the","of","is","and","to","in","that","we","for","an","are",
    "by","be","as","on","with","can","if","from","which","you","it",
    "this","then","at","have","all","not","one","has","or","that"
))

class IDFLoader:
    def __init__(self):
        self.path = ""
        self.idf_freq = {}
        self.median_idf = 0.0

    def set_new_path(self, new_idf_path):
        if self.path != new_idf_path:
            content = open(new_idf_path, 'rb').read().decode('utf-8')
            idf_freq = {}
            lines = content.split('\n')
            if lines and not lines[-1]:
                lines.pop(-1)
            for line in lines:
                word, freq = line.split(' ')
                idf_freq[word] = float(freq)
            median_idf = sorted(idf_freq.values())[len(idf_freq)/2]
            self.idf_freq = idf_freq
            self.median_idf = median_idf
            self.path = new_idf_path

    def get_idf(self):
        return self.idf_freq, self.median_idf

idf_loader = IDFLoader()
idf_loader.set_new_path(abs_path)

def set_idf_path(idf_path):
    new_abs_path = os.path.normpath(os.path.join(os.getcwd(), idf_path))
    if not os.path.exists(new_abs_path):
        raise Exception("jieba: path does not exist: " + new_abs_path)
    idf_loader.set_new_path(new_abs_path)

def set_stop_words(stop_words_path):
    global STOP_WORDS
    abs_path = os.path.normpath(os.path.join(os.getcwd(), stop_words_path))
    if not os.path.exists(abs_path):
        raise Exception("jieba: path does not exist: " + abs_path)
    content = open(abs_path,'rb').read().decode('utf-8')
    lines = content.split('\n')
    for line in lines:
        STOP_WORDS.add(line)

def extract_tags(sentence, topK=20, withWeight=False):
    global STOP_WORDS

    idf_freq, median_idf = idf_loader.get_idf()

    words = jieba.cut(sentence)
    freq = {}
    for w in words:
        if len(w.strip()) < 2:
            continue
        if w.lower() in STOP_WORDS:
            continue
        freq[w] = freq.get(w, 0.0) + 1.0
    total = sum(freq.values())
    freq = [(k,v/total) for k,v in freq.iteritems()]

    tf_idf_list = [(v*idf_freq.get(k,median_idf), k) for k,v in freq]
    st_list = sorted(tf_idf_list, reverse=True)

    if withWeight:
        tags = st_list[:topK]
    else:
        top_tuples = st_list[:topK]
        tags = [a[1] for a in top_tuples]
    return tags
