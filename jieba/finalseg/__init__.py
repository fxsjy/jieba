import regex
import os
import unicodedata
from math import log

MIN_FLOAT=-3.14e100

# Predefined words and patterns, ignore case, grouped
WHITE_LIST=regex.compile(ur"(?i)(AT&T|C\+\+|C#|[0-9]+\.[0-9]+)")

# All letters and numbers
LETTERS_AND_NUMBERS=regex.compile(ur"([\p{L}\p{N}]+)")

# Accent marks
IGNORED=regex.compile(ur"\p{Mn}+")

# Chinese ideograms, grouped
HAN=regex.compile(ur'(\p{Han}+)')

# Seperators, anything except letter and number
SEPERATOR=regex.compile(ur"[^\p{L}|\p{N}]+")

def load_model(f_name):
	_curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )
	prob_p_path = os.path.join(_curpath,f_name)
	tab = eval(open(prob_p_path,"rb").read())
	return tab

prob_start = load_model("prob_start.py")
prob_trans = load_model("prob_trans.py")
prob_emit = load_model("prob_emit.py")

def viterbi(obs, states, start_p, trans_p, emit_p):
	V = [{}] #tabular
	path = {}
	for y in states: #init
		V[0][y] = start_p[y] + emit_p[y].get(obs[0],MIN_FLOAT)
		path[y] = [y]
	for t in range(1,len(obs)):
		V.append({})
		newpath = {}
		for y in states:
			(prob,state ) = max([(V[t-1][y0] + trans_p[y0].get(y,MIN_FLOAT) + emit_p[y].get(obs[t],MIN_FLOAT) ,y0) for y0 in states ])
			V[t][y] =prob
			newpath[y] = path[state] + [y]
		path = newpath
	
	(prob, state) = max([(V[len(obs) - 1][y], y) for y in ('E','S')])
	
	return (prob, path[state])


def __cut(sentence):
	prob, pos_list =  viterbi(sentence,('B','M','E','S'), prob_start, prob_trans, prob_emit)
	begin, next = 0,0
	#print pos_list, sentence
	for i,char in enumerate(sentence):
		pos = pos_list[i]
		if pos=='B':
			begin = i
		elif pos=='E':
			yield sentence[begin:i+1]
			next = i+1
		elif pos=='S':
			yield char
			next = i+1
	if next<len(sentence):
		yield sentence[next:]

def cut(sentence):
	if type(sentence) is not unicode:
		try:
			sentence = sentence.decode('utf-8')
		except UnicodeError:
			sentence = sentence.decode('gb18030','ignore')
    
	# Remove accent marks
	sentence=IGNORED.sub("", unicodedata.normalize("NFKD", sentence))
    
	for s in WHITE_LIST.splititer(sentence):
		if WHITE_LIST.fullmatch(s):
			yield s
		else:
			blocks = HAN.split(s)
			for blk in blocks:
				if HAN.match(blk):
					for word in __cut(blk):
						yield word
				else:
					tmp = SEPERATOR.split(blk)
					for x in tmp:
						if x!="":
							yield x
