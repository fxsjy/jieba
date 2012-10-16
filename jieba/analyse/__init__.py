import jieba
import os

_curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )
f_name = os.path.join(_curpath,"idf.txt")
content = open(f_name,'rb').read().decode('utf-8')

idf_freq = {}
lines = content.split('\n')
for line in lines:
	word,freq = line.split(' ')
	idf_freq[word] = float(freq)
max_idf = max(idf_freq.values())

def extract_tags(sentence,topK=20):
	words = jieba.cut(sentence)
	freq = {}
	for w in words:
		if len(w.strip())<2: continue
		freq[w]=freq.get(w,0.0)+1.0
	total = sum(freq.values())
	freq = [(k,v/total) for k,v in freq.iteritems()]

	tf_idf_list = [(v * idf_freq.get(k,max_idf),k) for k,v in freq]
	st_list = sorted(tf_idf_list,reverse=True)

	top_tuples= st_list[:topK]
	tags = [a[1] for a in top_tuples]
	return tags

