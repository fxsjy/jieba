# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import shutil
import sys
import tempfile
import unittest

sys.path.append('../')

from jieba.analyse import TFIDF
from jieba.analyse.tfidf import IDFLoader


class IDFReloadTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp(prefix='jieba-idf-')
        self.original_path = self.write_file('original.txt', '北京 2\n上海 3\n')
        self.replacement_path = os.path.join(self.directory, 'replacement.txt')

    def tearDown(self):
        shutil.rmtree(self.directory)

    def write_file(self, name, text):
        path = os.path.join(self.directory, name)
        with open(path, 'wb') as stream:
            stream.write(text.encode('utf-8'))
        return path

    def testFailedParsePreservesLoadedIDF(self):
        loader = IDFLoader(self.original_path)
        original_idf, original_median = loader.get_idf()
        self.write_file('replacement.txt', '上海 8\ninvalid row with extras\n')
        with self.assertRaises(ValueError):
            loader.set_new_path(self.replacement_path)
        self.assertEqual(loader.path, self.original_path)
        self.assertEqual(loader.get_idf(), (original_idf, original_median))
        self.assertIs(loader.get_idf()[0], original_idf)

    def assertRepairedFileLoads(self, extractor):
        self.write_file('replacement.txt', '北京 6\n上海 7\n')
        extractor.set_idf_path(self.replacement_path)
        self.assertEqual(extractor.extract_tags('北京 上海', withWeight=True),
                         [('上海', 3.5), ('北京', 3.0)])

    def testRetryAfterMalformedRow(self):
        extractor = TFIDF(self.original_path)
        original_tags = extractor.extract_tags('北京 上海', withWeight=True)
        self.write_file('replacement.txt', '上海 8\ninvalid row with extras\n')
        with self.assertRaises(ValueError):
            extractor.set_idf_path(self.replacement_path)
        self.assertEqual(extractor.extract_tags('北京 上海', withWeight=True),
                         original_tags)
        self.assertRepairedFileLoads(extractor)

    def testRetryAfterInvalidFrequency(self):
        extractor = TFIDF(self.original_path)
        self.write_file('replacement.txt', '上海 8\n北京 invalid\n')
        with self.assertRaises(ValueError):
            extractor.set_idf_path(self.replacement_path)
        self.assertRepairedFileLoads(extractor)

    def testRetryAfterInvalidEncoding(self):
        extractor = TFIDF(self.original_path)
        with open(self.replacement_path, 'wb') as stream:
            stream.write(b'\xff')
        with self.assertRaises(UnicodeDecodeError):
            extractor.set_idf_path(self.replacement_path)
        self.assertRepairedFileLoads(extractor)

    def testRetryAfterEmptyFile(self):
        extractor = TFIDF(self.original_path)
        self.write_file('replacement.txt', '')
        with self.assertRaises(IndexError):
            extractor.set_idf_path(self.replacement_path)
        self.assertRepairedFileLoads(extractor)

    def testRetryAfterMissingFile(self):
        loader = IDFLoader(self.original_path)
        with self.assertRaises(IOError):
            loader.set_new_path(self.replacement_path)
        self.write_file('replacement.txt', '北京 6\n上海 7\n')
        loader.set_new_path(self.replacement_path)
        self.assertEqual(loader.get_idf(), ({'北京': 6.0, '上海': 7.0}, 7.0))


if __name__ == '__main__':
    unittest.main()
