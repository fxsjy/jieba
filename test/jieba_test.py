#-*-coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys
sys.path.append("../")
import unittest
import types
import jieba
if sys.version_info[0] > 2:
    from imp import reload

jieba.initialize()


test_contents = [
    "这是一个伸手不见五指的黑夜。我叫孙悟空，我爱北京，我爱Python和C++。",
    "我不喜欢日本和服。",
    "雷猴回归人间。",
    "工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作",
    "我需要廉租房",
    "永和服装饰品有限公司",
    "我爱北京天安门",
    "abc",
    "隐马尔可夫",
    "雷猴是个好网站",
    "“Microsoft”一词由“MICROcomputer（微型计算机）”和“SOFTware（软件）”两部分组成",
    "草泥马和欺实马是今年的流行词汇",
    "伊藤洋华堂总府店",
    "中国科学院计算技术研究所",
    "罗密欧与朱丽叶",
    "我购买了道具和服装",
    "PS: 我觉得开源有一个好处，就是能够敦促自己不断改进，避免敞帚自珍",
    "湖北省石首市",
    "湖北省十堰市",
    "总经理完成了这件事情",
    "电脑修好了",
    "做好了这件事情就一了百了了",
    "人们审美的观点是不同的",
    "我们买了一个美的空调",
    "线程初始化时我们要注意",
    "一个分子是由好多原子组织成的",
    "祝你马到功成",
    "他掉进了无底洞里",
    "中国的首都是北京",
    "孙君意",
    "外交部发言人马朝旭",
    "领导人会议和第四届东亚峰会",
    "在过去的这五年",
    "还需要很长的路要走",
    "60周年首都阅兵",
    "你好人们审美的观点是不同的",
    "买水果然后来世博园",
    "买水果然后去世博园",
    "但是后来我才知道你是对的",
    "存在即合理",
    "的的的的的在的的的的就以和和和",
    "I love你，不以为耻，反以为rong",
    "因",
    "",
    "hello你好人们审美的观点是不同的",
    "很好但主要是基于网页形式",
    "hello你好人们审美的观点是不同的",
    "为什么我不能拥有想要的生活",
    "后来我才",
    "此次来中国是为了",
    "使用了它就可以解决一些问题",
    ",使用了它就可以解决一些问题",
    "其实使用了它就可以解决一些问题",
    "好人使用了它就可以解决一些问题",
    "是因为和国家",
    "老年搜索还支持",
    "干脆就把那部蒙人的闲法给废了拉倒！RT @laoshipukong : 27日，全国人大常委会第三次审议侵权责任法草案，删除了有关医疗损害责任“举证倒置”的规定。在医患纠纷中本已处于弱势地位的消费者由此将陷入万劫不复的境地。 ",
    "大",
    "",
    "他说的确实在理",
    "长春市长春节讲话",
    "结婚的和尚未结婚的",
    "结合成分子时",
    "旅游和服务是最好的",
    "这件事情的确是我的错",
    "供大家参考指正",
    "哈尔滨政府公布塌桥原因",
    "我在机场入口处",
    "邢永臣摄影报道",
    "BP神经网络如何训练才能在分类时增加区分度？",
    "南京市长江大桥",
    "应一些使用者的建议，也为了便于利用NiuTrans用于SMT研究",
    '长春市长春药店',
    '邓颖超生前最喜欢的衣服',
    '胡锦涛是热爱世界和平的政治局常委',
    '程序员祝海林和朱会震是在孙健的左面和右面, 范凯在最右面.再往左是李松洪',
    '一次性交多少钱',
    '两块五一套，三块八一斤，四块七一本，五块六一条',
    '小和尚留了一个像大和尚一样的和尚头',
    '我是中华人民共和国公民;我爸爸是共和党党员; 地铁和平门站',
    '张晓梅去人民医院做了个B超然后去买了件T恤',
    'AT&T是一件不错的公司，给你发offer了吗？',
    'C++和c#是什么关系？11+122=133，是吗？PI=3.14159',
    '你认识那个和主席握手的的哥吗？他开一辆黑色的士。',
    '枪杆子中出政权']


class JiebaTestCase(unittest.TestCase):
    def setUp(self):
        reload(jieba)

    def tearDown(self):
        pass

    def testDefaultCut(self):
        for content in test_contents:
            result = jieba.cut(content)
            assert isinstance(result, types.GeneratorType), "Test DefaultCut Generator error"
            result = list(result)
            assert isinstance(result, list), "Test DefaultCut error on content: %s" % content
            print(" , ".join(result), file=sys.stderr)
        print("testDefaultCut", file=sys.stderr)

    def testCutAll(self):
        for content in test_contents:
            result = jieba.cut(content, cut_all=True)
            assert isinstance(result, types.GeneratorType), "Test CutAll Generator error"
            result = list(result)
            assert isinstance(result, list), "Test CutAll error on content: %s" % content
            print(" , ".join(result), file=sys.stderr)
        print("testCutAll", file=sys.stderr)

    def testSetDictionary(self):
        jieba.set_dictionary("foobar.txt")
        for content in test_contents:
            result = jieba.cut(content)
            assert isinstance(result, types.GeneratorType), "Test SetDictionary Generator error"
            result = list(result)
            assert isinstance(result, list), "Test SetDictionary error on content: %s" % content
            print(" , ".join(result), file=sys.stderr)
        print("testSetDictionary", file=sys.stderr)

    def testCutForSearch(self):
        for content in test_contents:
            result = jieba.cut_for_search(content)
            assert isinstance(result, types.GeneratorType), "Test CutForSearch Generator error"
            result = list(result)
            assert isinstance(result, list), "Test CutForSearch error on content: %s" % content
            print(" , ".join(result), file=sys.stderr)
        print("testCutForSearch", file=sys.stderr)

    def testPosseg(self):
        import jieba.posseg as pseg
        for content in test_contents:
            result = pseg.cut(content)
            assert isinstance(result, types.GeneratorType), "Test Posseg Generator error"
            result = list(result)
            assert isinstance(result, list), "Test Posseg error on content: %s" % content
            print(" , ".join([w.word + " / " + w.flag for w in result]), file=sys.stderr)
        print("testPosseg", file=sys.stderr)

    def testTokenize(self):
        for content in test_contents:
            result = jieba.tokenize(content)
            assert isinstance(result, types.GeneratorType), "Test Tokenize Generator error"
            result = list(result)
            assert isinstance(result, list), "Test Tokenize error on content: %s" % content
            for tk in result:
                print("word %s\t\t start: %d \t\t end:%d" % (tk[0],tk[1],tk[2]), file=sys.stderr)
        print("testTokenize", file=sys.stderr)

    def testDefaultCut_NOHMM(self):
        for content in test_contents:
            result = jieba.cut(content,HMM=False)
            assert isinstance(result, types.GeneratorType), "Test DefaultCut Generator error"
            result = list(result)
            assert isinstance(result, list), "Test DefaultCut error on content: %s" % content
            print(" , ".join(result), file=sys.stderr)
        print("testDefaultCut_NOHMM", file=sys.stderr)

    def testPosseg_NOHMM(self):
        import jieba.posseg as pseg
        for content in test_contents:
            result = pseg.cut(content,HMM=False)
            assert isinstance(result, types.GeneratorType), "Test Posseg Generator error"
            result = list(result)
            assert isinstance(result, list), "Test Posseg error on content: %s" % content
            print(" , ".join([w.word + " / " + w.flag for w in result]), file=sys.stderr)
        print("testPosseg_NOHMM", file=sys.stderr)

    def testTokenize_NOHMM(self):
        for content in test_contents:
            result = jieba.tokenize(content,HMM=False)
            assert isinstance(result, types.GeneratorType), "Test Tokenize Generator error"
            result = list(result)
            assert isinstance(result, list), "Test Tokenize error on content: %s" % content
            for tk in result:
                print("word %s\t\t start: %d \t\t end:%d" % (tk[0],tk[1],tk[2]), file=sys.stderr)
        print("testTokenize_NOHMM", file=sys.stderr)

    def testCutForSearch_NOHMM(self):
        for content in test_contents:
            result = jieba.cut_for_search(content,HMM=False)
            assert isinstance(result, types.GeneratorType), "Test CutForSearch Generator error"
            result = list(result)
            assert isinstance(result, list), "Test CutForSearch error on content: %s" % content
            print(" , ".join(result), file=sys.stderr)
        print("testCutForSearch_NOHMM", file=sys.stderr)

if __name__ == "__main__":
    unittest.main()
