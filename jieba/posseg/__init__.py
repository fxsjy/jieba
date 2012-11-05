import re
import os
import viterbi

def load_model(f_name):
	_curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )
	prob_p_path = os.path.join(_curpath,f_name)
	if f_name.endswith(".py"):
		return eval(open(prob_p_path,"rb").read())
	else:
		result = set()
		for line in open(prob_p_path,"rb"):
			result.add(line.strip().decode('utf-8'))
		return result


prob_start = load_model("prob_start.py")
prob_trans = load_model("prob_trans.py")
prob_emit = load_model("prob_emit.py")
char_state_tab = load_model("char_state_tab.py")


def __cut(sentence):
	prob, pos_list =  viterbi.viterbi(sentence,char_state_tab, prob_start, prob_trans, prob_emit)
	begin, next = 0,0

	for i,char in enumerate(sentence):
		pos = pos_list[i][0]
		if pos=='B':
			begin = i
		elif pos=='E':
			yield sentence[begin:i+1]+"/"+pos_list[i][1]
			next = i+1
		elif pos=='S':
			yield char+"/"+pos_list[i][1]
			next = i+1
	if next<len(sentence):
		yield sentence[next:]+"/"+pos_list[next][1]

def cut(sentence):
	if not ( type(sentence) is unicode):
		try:
			sentence = sentence.decode('utf-8')
		except:
			sentence = sentence.decode('gbk','ignore')
	re_han, re_skip = re.compile(ur"([\u4E00-\u9FA5]+)"), re.compile(ur"[^a-zA-Z0-9+#\n%]")
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
