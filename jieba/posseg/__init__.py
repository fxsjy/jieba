import re
import os
import viterbi
import jieba
import sys
default_encoding = sys.getfilesystemencoding()

def load_model(f_name):
	_curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )
	prob_p_path = os.path.join(_curpath,f_name)
	if f_name.endswith(".py"):
		return eval(open(prob_p_path,"rb").read())
	else:
		result = {}
		for line in open(prob_p_path,"rb"):
			line = line.strip()
			if line=="":continue
			word, _, tag = line.split(' ')
			result[word.decode('utf-8')]=tag
		return result


prob_start = load_model("prob_start.py")
prob_trans = load_model("prob_trans.py")
prob_emit = load_model("prob_emit.py")
char_state_tab = load_model("char_state_tab.py")
word_tag_tab = load_model("../dict.txt")

class pair(object):
	def __init__(self,word,flag):
		self.word = word
		self.flag = flag

	def __unicode__(self):
		return self.word+u"/"+self.flag

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return self.__unicode__().encode(default_encoding)

	def encode(self,arg):
		return self.__unicode__().encode(arg)

def __cut(sentence):
	prob, pos_list =  viterbi.viterbi(sentence,char_state_tab, prob_start, prob_trans, prob_emit)
	begin, next = 0,0

	for i,char in enumerate(sentence):
		pos = pos_list[i][0]
		if pos=='B':
			begin = i
		elif pos=='E':
			yield pair(sentence[begin:i+1], pos_list[i][1])
			next = i+1
		elif pos=='S':
			yield pair(char,pos_list[i][1])
			next = i+1
	if next<len(sentence):
		yield pair(sentence[next:], pos_list[next][1] )

def __cut_DAG(sentence):
	DAG = jieba.get_DAG(sentence)
	route ={}
	jieba.calc(sentence,DAG,0,route=route)
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
					yield pair(buf,word_tag_tab.get(buf,'x'))
					buf=u''
				else:
					regognized = __cut(buf)
					for t in regognized:
						yield t
					buf=u''
			yield pair(l_word,word_tag_tab.get(l_word,'x'))
		x =y

	if len(buf)>0:
		if len(buf)==1:
			yield pair(buf,word_tag_tab.get(buf,'x'))
		else:
			regognized = __cut(buf)
			for t in regognized:
				yield t


def cut(sentence):
	if not ( type(sentence) is unicode):
		try:
			sentence = sentence.decode('utf-8')
		except:
			sentence = sentence.decode('gbk','ignore')
	re_han, re_skip = re.compile(ur"([\u4E00-\u9FA5]+)"), re.compile(ur"[^a-zA-Z0-9+#\n%]")
	re_eng,re_num = re.compile(ur"[a-zA-Z+#]+"), re.compile(ur"[0-9]+")
	blocks = re_han.split(sentence)

	for blk in blocks:
		if re_han.match(blk):
				for word in __cut_DAG(blk):
					yield word
		else:
			tmp = re_skip.split(blk)
			for x in tmp:
				if x!="":
					if re_num.match(x):
						yield pair(x,'m')
					elif re_eng.match(x):
						yield pair(x,'eng')
					else:
						yield pair(x,'x')
