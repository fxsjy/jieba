import re
import os
import viterbi
import jieba
import sys
import prob_start
import prob_trans
import prob_emit
import char_state_tab

default_encoding = sys.getfilesystemencoding()

def load_model(f_name):
    _curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )
    prob_p_path = os.path.join(_curpath,f_name)
    if f_name.endswith(".py"):
        return eval(open(prob_p_path,"rb").read())
    else:
        result = {}
        for line in open(f_name,"rb"):
            line = line.strip()
            if line=="":continue
            word, _, tag = line.split(' ')
            result[word.decode('utf-8')]=tag
        return result

word_tag_tab = load_model(jieba.get_abs_path_dict())

if jieba.user_word_tag_tab:
    word_tag_tab.update(jieba.user_word_tag_tab)

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
    prob, pos_list =  viterbi.viterbi(sentence,char_state_tab.P, prob_start.P, prob_trans.P, prob_emit.P)
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

def __cut_detail(sentence):
    re_han, re_skip = re.compile(ur"([\u4E00-\u9FA5]+)"), re.compile(ur"([\.0-9]+|[a-zA-Z0-9]+)")
    re_eng,re_num = re.compile(ur"[a-zA-Z0-9]+"), re.compile(ur"[\.0-9]+")
    blocks = re_han.split(sentence)
    for blk in blocks:
        if re_han.match(blk):
                for word in __cut(blk):
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
                    if not (buf in jieba.FREQ):
                        regognized = __cut_detail(buf)
                        for t in regognized:
                            yield t
                    else:
                        for elem in buf:
                            yield pair(elem,word_tag_tab.get(elem,'x'))
                    buf=u''
            yield pair(l_word,word_tag_tab.get(l_word,'x'))
        x =y

    if len(buf)>0:
        if len(buf)==1:
            yield pair(buf,word_tag_tab.get(buf,'x'))
        else:
            if not (buf in jieba.FREQ):
                regognized = __cut_detail(buf)
                for t in regognized:
                    yield t
            else:
                for elem in buf:
                    yield pair(elem,word_tag_tab.get(elem,'x'))

def __cut_internal(sentence):
    if not ( type(sentence) is unicode):
        try:
            sentence = sentence.decode('utf-8')
        except:
            sentence = sentence.decode('gbk','ignore')
    re_han, re_skip = re.compile(ur"([\u4E00-\u9FA5a-zA-Z0-9+#&\._]+)"), re.compile(ur"(\r\n|\s)")
    re_eng,re_num = re.compile(ur"[a-zA-Z0-9]+"), re.compile(ur"[\.0-9]+")
    blocks = re_han.split(sentence)
    for blk in blocks:
        if re_han.match(blk):
                for word in __cut_DAG(blk):
                    yield word
        else:
            tmp = re_skip.split(blk)
            for x in tmp:
                if re_skip.match(x):
                    yield pair(x,'x')
                else:
                    for xx in x:
                        if re_num.match(xx):
                            yield pair(xx,'m')
                        elif re_eng.match(x):
                            yield pair(xx,'eng')
                        else:
                            yield pair(xx,'x')

def __lcut_internal(sentence):
    return list(__cut_internal(sentence))

def cut(sentence):
    if (not hasattr(jieba,'pool')) or (jieba.pool==None):
        for w in __cut_internal(sentence):
            yield w
    else:
        parts = re.compile('([\r\n]+)').split(sentence)
        result = jieba.pool.map(__lcut_internal,parts)    
        for r in result:
            for w in r:
                yield w

