import re
import math
import os,sys
import pprint
import finalseg

FREQ = {}
total =0

def gen_trie(f_name):
	global total
	trie = {}
	for line in open(f_name):
		word,freq = line.strip().split(" ")
		word = word.decode('utf-8')
		freq = int(freq)
		FREQ[word] = freq
		total+=freq
		p = trie
		for c in word:
			if not c in p:
				p[c] ={}
			p = p[c]
		p['']='' #ending flag
	return trie

_curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )

print >> sys.stderr, "Building Trie..."
trie = gen_trie(os.path.join(_curpath,"dict.txt"))
FREQ = dict([(k,float(v)/total) for k,v in FREQ.iteritems()]) #normalize
min_freq = min(FREQ.itervalues())
#print min_freq
print >> sys.stderr,"Trie has been built succesfully."


def __cut_all(sentence):
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
				p=trie
		else:
			p = trie
			i+=1
			j=i

def calc(sentence,DAG,idx,route):
	if idx in route:
		return route[idx]
	if idx>=len(sentence):
		return (1.0,'')
	next = DAG[idx]
	best = max([ ( FREQ.get(sentence[idx:x+1],min_freq) * calc(sentence,DAG,x+1,route=route)[0],x )for x in next ])
	route[idx]=best
	return best


def __cut_DAG(sentence):
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
	#pprint.pprint(DAG)
	route ={}
	calc(sentence,DAG,0,route=route)
	x = 0
	buf =u''
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
					regognized = finalseg.__cut(buf)
					for t in regognized:
						yield t
					buf=u''
			yield l_word		
		x =y

	if len(buf)>0:
		if len(buf)==1:
			yield buf
		else:
			regognized = finalseg.__cut(buf)
			for t in regognized:
				yield t


def cut(sentence,cut_all=False):
	if not ( type(sentence) is unicode):
		try:
			sentence = sentence.decode('utf-8')
		except:
			sentence = sentence.decode('gbk','ignore')
	re_han, re_skip = re.compile(ur"([\u4E00-\u9FA5]+)"), re.compile(ur"[^a-zA-Z0-9+#\n]")
	blocks = re_han.split(sentence)
	cut_block = __cut_DAG
	if cut_all:
		cut_block = __cut_all
	for blk in blocks:
		if re_han.match(blk):
				#pprint.pprint(__cut_DAG(blk))
				for word in cut_block(blk):
					yield word
		else:
			tmp = re_skip.split(blk)
			for x in tmp:
				if x!="":
					yield x
