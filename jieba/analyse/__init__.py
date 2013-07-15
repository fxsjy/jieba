import jieba
import os
try:
	from analyzer import ChineseAnalyzer
except ImportError:
	pass

_curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )
f_name = os.path.join(_curpath,"idf.txt")
content = open(f_name,'rb').read().decode('utf-8')

idf_freq = {}
lines = content.split('\n')
for line in lines:
    word,freq = line.split(' ')
    idf_freq[word] = float(freq)

median_idf = sorted(idf_freq.values())[len(idf_freq)/2]
stop_words= set([
"the","of","is","and","to","in","that","we","for","an","are","by","be","as","on","with","can","if","from","which","you","it","this","then","at","have","all","not","one","has","or","that"
])

def extract_tags(sentence,topK=20):
    words = jieba.cut(sentence)
    freq = {}
    for w in words:
        if len(w.strip())<2: continue
        if w.lower() in stop_words: continue
        freq[w]=freq.get(w,0.0)+1.0
    total = sum(freq.values())
    freq = [(k,v/total) for k,v in freq.iteritems()]

    tf_idf_list = [(v * idf_freq.get(k,median_idf),k) for k,v in freq]
    st_list = sorted(tf_idf_list,reverse=True)

    top_tuples= st_list[:topK]
    tags = [a[1] for a in top_tuples]
    return tags
