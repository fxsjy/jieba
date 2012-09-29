import re
import math
import os,sys
import pprint

def gen_trie(f_name):
	trie = {}
	for line in open(f_name):
		word,freq = line.strip().split(" ")
		word = word.decode('utf-8')
		p = trie
		for c in word:
			if not c in p:
				p[c] ={}
			p = p[c]
		p['']='' #ending flag
	return trie

_curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )
print >> sys.stderr, "loading dictionary..."
trie = gen_trie(os.path.join(_curpath,"dict.txt"))
print >> sys.stderr,"done."

def __cut(sentence):
	N = len(sentence)
	i,j=0,0
	p = trie
	while i<N:
		c = sentence[j]
		if c in p:
			p = p[c]
			if '' in p:
				yield sentence[i:j+1]
			j+=1
			if j>=N:
				i+=1
				j=i
		else:
			p = trie
			i+=1
			j=i

def cut(sentence):
	if not ( type(sentence) is unicode):
		try:
			sentence = sentence.decode('utf-8')
		except:
			sentence = sentence.decode('gbk','ignore')
	re_han, re_skip = re.compile(ur"([\u4E00-\u9FA5]+)"), re.compile(ur"[^a-zA-Z0-9+#\n]")
	blocks = re_han.split(sentence)
	
	for blk in blocks:
		if re_han.match(blk):
				for word in __cut(blk):
					yield word
		else:
			tmp = re_skip.split(blk)
			for x in tmp:
				if x!="":
					yield x
