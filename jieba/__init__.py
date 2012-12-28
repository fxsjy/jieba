import re
import regex
import unicodedata
import math
import os,sys
import pprint
import finalseg
import time
import tempfile
import marshal
from math import log

from finalseg import WHITE_LIST, LETTERS_AND_NUMBERS, IGNORED, HAN, SEPERATOR

FREQ = {}
total =0.0

def gen_trie(f_name):
	lfreq = {}
	trie = {}
	ltotal = 0.0
	content = open(f_name,'rb').read().decode('utf-8')
	for line in content.split("\n"):
		word,freq,_ = line.split(" ")
		freq = float(freq)
		lfreq[word] = freq
		ltotal+=freq
		p = trie
		for c in word:
			if not c in p:
				p[c] ={}
			p = p[c]
		p['']='' #ending flag
	return trie, lfreq,ltotal


_curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )

print >> sys.stderr, "Building Trie..."
t1 = time.time()
cache_file = os.path.join(tempfile.gettempdir(),"jieba.cache")
load_from_cache_fail = True
if os.path.exists(cache_file) and os.path.getmtime(cache_file)>os.path.getmtime(os.path.join(_curpath,"dict.txt")):
	print >> sys.stderr, "loading model from cache"
	try:
		trie,FREQ,total,min_freq = marshal.load(open(cache_file,'rb'))
		load_from_cache_fail = False
	except:
		load_from_cache_fail = True

if load_from_cache_fail:
	trie,FREQ,total = gen_trie(os.path.join(_curpath,"dict.txt"))
	FREQ = dict([(k,log(float(v)/total)) for k,v in FREQ.iteritems()]) #normalize
	min_freq = min(FREQ.itervalues())
	print >> sys.stderr, "dumping model to file cache"
	marshal.dump((trie,FREQ,total,min_freq),open(cache_file,'wb'))

print >> sys.stderr, "loading model cost ", time.time() - t1, "seconds."
print >> sys.stderr, "Trie has been built succesfully."


def __cut_all(sentence):
	dag = get_DAG(sentence)
	old_j = -1
	for k,L in dag.iteritems():
		if len(L)==1 and k>old_j:
			yield sentence[k:L[0]+1]
			old_j = L[0] 
		else:
			for j in L:
				if j>k:
					yield sentence[k:j+1]
					old_j = j

def calc(sentence,DAG,idx,route):
	N = len(sentence)
	route[N] = (1.0,'')
	for idx in xrange(N-1,-1,-1):
		candidates = [ ( FREQ.get(sentence[idx:x+1],min_freq) + route[x+1][0],x ) for x in DAG[idx] ]
		route[idx] = max(candidates)

def get_DAG(sentence):
	N = len(sentence)
	i,j=0,0
	p = trie
	DAG = {}
	while i<N:
		c = sentence[j]
		if c in p:
			p = p[c]
			if '' in p:
				if not i in DAG:
					DAG[i]=[]
				DAG[i].append(j)
			j+=1
			if j>=N:
				i+=1
				j=i
				p=trie
		else:
			p = trie
			i+=1
			j=i
	for i in xrange(len(sentence)):
		if not i in DAG:
			DAG[i] =[i]
	return DAG

def __cut_DAG(sentence):
	DAG = get_DAG(sentence)
	route ={}
	calc(sentence,DAG,0,route=route)
	x = 0
	buf =u''
	N = len(sentence)
	while x<N:
		y = route[x][1]+1
		l_word = sentence[x:y]
		if y-x==1:
			buf+= l_word
		else:
			if len(buf)>0:
				if len(buf)==1:
					yield buf
					buf=u''
				else:
					regognized = finalseg.cut(buf)
					for t in regognized:
						yield t
					buf=u''
			yield l_word		
		x =y

	if len(buf)>0:
		if len(buf)==1:
			yield buf
		else:
			regognized = finalseg.cut(buf)
			for t in regognized:
				yield t


def cut(sentence,cut_all=False):
	if not ( type(sentence) is unicode):
		try:
			sentence = sentence.decode('utf-8')
		except UnicodeError:
			sentence = sentence.decode('gb18030','ignore')

	# Remove accent marks
	sentence=IGNORED.sub("", unicodedata.normalize("NFKD", sentence))

	re_han, re_skip = LETTERS_AND_NUMBERS, SEPERATOR
	if cut_all:
		re_han, re_skip = HAN, SEPERATOR
	cut_block = __cut_DAG
	if cut_all:
		cut_block = __cut_all
	for s in WHITE_LIST.splititer(sentence):
		if WHITE_LIST.fullmatch(s):
			yield s
		else:
			for blk in re_han.splititer(s):
				if re_han.match(blk):
						#pprint.pprint(__cut_DAG(blk))
						for word in cut_block(blk):
							yield word
				else:
					for x in re_skip.splititer(blk):
						if x!="":
							yield x

def cut_for_search(sentence):
	words = cut(sentence)
	for w in words:
		if len(w)>2:
			for i in xrange(len(w)-1):
				gram2 = w[i:i+2]
				if gram2 in FREQ:
					yield gram2
		if len(w)>3:
			for i in xrange(len(w)-2):
				gram3 = w[i:i+3]
				if gram3 in FREQ:
					yield gram3
		yield w

def load_userdict(f):
	global trie,total,FREQ
	if isinstance(f, (str, unicode)):
		f = open(f, 'rb')
	content = f.read().decode('utf-8')
	for line in content.split("\n"):
		if line.rstrip()=='': continue
		word,freq = line.split(" ")
		freq = float(freq)
		FREQ[word] = log(freq / total)
		p = trie
		for c in word:
			if not c in p:
				p[c] ={}
			p = p[c]
		p['']='' #ending flag
