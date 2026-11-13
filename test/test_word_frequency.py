# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import os
import shutil
import tempfile
import unittest

import jieba


class WordFrequencyTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp_dir)
        dictionary = os.path.join(self.tmp_dir, 'dict.txt')
        with io.open(dictionary, 'w', encoding='utf-8') as f:
            f.write('甲 10 n\n乙 10 n\n甲乙 1 n\n无关 50 n\n')
        self.tokenizer = jieba.Tokenizer(dictionary)
        self.tokenizer.tmp_dir = self.tmp_dir
        self.tokenizer.initialize()

    def test_readding_word_preserves_segmentation(self):
        self.assertEqual(self.tokenizer.lcut('甲乙', HMM=False), ['甲', '乙'])
        self.tokenizer.add_word('无关', 50)
        self.assertEqual(self.tokenizer.lcut('甲乙', HMM=False), ['甲', '乙'])
        self.assertEqual(self.tokenizer.total, 71)

    def test_replacing_frequency_updates_total_by_difference(self):
        for freq in (5, 80, 1):
            self.tokenizer.add_word('无关', freq)
            self.assertEqual(self.tokenizer.FREQ['无关'], freq)
            self.assertEqual(self.tokenizer.total, 21 + freq)

    def test_loading_user_dictionary_twice_is_idempotent(self):
        for _ in range(2):
            self.tokenizer.load_userdict(io.BytesIO('无关 50 n\n甲乙丙 3 n\n'.encode('utf-8')))
            self.assertEqual(self.tokenizer.total, 74)
            self.assertEqual(self.tokenizer.total, sum(self.tokenizer.FREQ.values()))
            self.assertEqual(self.tokenizer.FREQ['甲乙丙'], 3)
            self.assertEqual(self.tokenizer.lcut('甲乙', HMM=False), ['甲', '乙'])


if __name__ == '__main__':
    unittest.main()
