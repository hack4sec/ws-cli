#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, pytest

wrpath   = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes')
sys.path.append(wrpath + '/classes/models')
sys.path.append(wrpath + '/classes/kernel')
sys.path.append(testpath + '/classes')

from classes.Registry import Registry
from libs.common import *


class Test_Registry(object):
    model = None

    # Проверка установки и получения значения из реестра
    def test_set_and_get(self):
        with pytest.raises(KeyError):
            Registry().get('aaa')
        Registry().set('aaa', 'bbb')
        assert Registry().get('aaa') == 'bbb'
