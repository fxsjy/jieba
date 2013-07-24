import re
import os
import marshal

MIN_FLOAT=-3.14e100

PROB_START_P = "prob_start.p"
PROB_TRANS_P = "prob_trans.p"
PROB_EMIT_P = "prob_emit.p"


PrevStatus = {
    'B':('E','S'),
    'M':('M','B'),
    'S':('S','E'),
    'E':('B','M')
}

def load_model():
    _curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )

    start_p = {}
    abs_path = os.path.join(_curpath, PROB_START_P)
    with open(abs_path, mode='rb') as f:
        start_p = marshal.load(f)
    f.closed
    
    trans_p = {}
    abs_path = os.path.join(_curpath, PROB_TRANS_P)
    with open(abs_path, 'rb') as f:
        trans_p = marshal.load(f)
    f.closed
    
    emit_p = {}
    abs_path = os.path.join(_curpath, PROB_EMIT_P)
    with file(abs_path, 'rb') as f:
        emit_p = marshal.load(f)
    f.closed

    return start_p, trans_p, emit_p

start_P, trans_P, emit_P = load_model()    

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
            em_p = emit_p[y].get(obs[t],MIN_FLOAT)
            (prob,state ) = max([(V[t-1][y0] + trans_p[y0].get(y,MIN_FLOAT) + em_p ,y0) for y0 in PrevStatus[y] ])
            V[t][y] =prob
            newpath[y] = path[state] + [y]
        path = newpath
    
    (prob, state) = max([(V[len(obs) - 1][y], y) for y in ('E','S')])
    
    return (prob, path[state])


def __cut(sentence):
    global emit_P
    prob, pos_list =  viterbi(sentence,('B','M','E','S'), start_P, trans_P, emit_P)
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
    if not ( type(sentence) is unicode):
        try:
            sentence = sentence.decode('utf-8')
        except:
            sentence = sentence.decode('gbk','ignore')
    re_han, re_skip = re.compile(ur"([\u4E00-\u9FA5]+)"), re.compile(ur"(\d+\.\d+|[a-zA-Z0-9]+)")
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
