# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for CombineGenetator
"""

import sys
import os

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes')
sys.path.append(wrpath + '/classes/models')
sys.path.append(wrpath + '/classes/kernel')
sys.path.append(testpath + '/classes')

from classes.CombineGenerator import CombineGenerator
from libs.common import file_put_contents

class Test_CombineGenerator(object):
    """Unit tests for CombineGenetator"""
    def test_gen_dm_no_parts(self):
        test_set = [
            'aaa0', 'bbb0', 'ccc0',
            'aaa1', 'bbb1', 'ccc1',
            'aaa2', 'bbb2', 'ccc2',
            'aaa3', 'bbb3', 'ccc3',
            'aaa4', 'bbb4', 'ccc4',
            'aaa5', 'bbb5', 'ccc5',
            'aaa6', 'bbb6', 'ccc6',
            'aaa7', 'bbb7', 'ccc7',
            'aaa8', 'bbb8', 'ccc8',
            'aaa9', 'bbb9', 'ccc9',
        ]
        test_set.sort()

        file_put_contents('/tmp/test.txt', 'aaa\nbbb\nccc')
        gen = CombineGenerator('?d,1,1', '/tmp/test.txt', parts=0, part=0, template='%d%%m%')

        for test_phrase in test_set:
            assert gen.get() == test_phrase
        assert gen.get() is None

    def test_gen_md_no_parts(self):
        test_set = [
            '0aaa', '1aaa', '2aaa', '3aaa', '4aaa', '5aaa', '6aaa', '7aaa', '8aaa', '9aaa',
            '0bbb', '1bbb', '2bbb', '3bbb', '4bbb', '5bbb', '6bbb', '7bbb', '8bbb', '9bbb',
            '0ccc', '1ccc', '2ccc', '3ccc', '4ccc', '5ccc', '6ccc', '7ccc', '8ccc', '9ccc',
        ]

        file_put_contents('/tmp/test.txt', 'aaa\nbbb\nccc')
        gen = CombineGenerator('?d,1,1', '/tmp/test.txt', parts=0, part=0, template='%m%%d%')
        for test_phrase in test_set:
            assert gen.get() == test_phrase
        assert gen.get() is None

    def test_gen_md_part(self):
        test_set = [
            '0bbb', '1bbb', '2bbb', '3bbb', '4bbb', '5bbb', '6bbb', '7bbb', '8bbb', '9bbb',
        ]
        test_set.sort()

        file_put_contents('/tmp/test.txt', 'aaa\nbbb\nccc')
        gen = CombineGenerator('?d,1,1', '/tmp/test.txt', parts=3, part=2, template='%m%%d%')
        for test_phrase in test_set:
            assert gen.get() == test_phrase
        assert gen.get() is None
