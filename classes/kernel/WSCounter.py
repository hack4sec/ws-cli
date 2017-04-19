# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Alexey Meshcheryakov <tank1st99@gmail.com>

Kernel class of work counter for all modules
"""
from __future__ import division
import sys
import time

from libs.common import secs_to_text, nformat


class WSCounter(object):
    """ Kernel class of work counter for all modules """
    counter = 0
    last_point_time = 0
    last_point_count = 0

    def __init__(self, point, new_str, _all=0):
        self.point = point
        self.new_str = new_str
        self.all = _all
        self.start_time = int(time.time())
        self.last_point_time = int(time.time())

    def up(self):
        """ Up counter, print result if need """
        self.counter += 1

        if self.counter%self.point == 0:
            sys.stdout.write('.')

        if self.counter%self.new_str == 0:
            if self.all == 0:
                print "({0})".format(self.counter)
            else:
                percents = round(self.counter/(self.all/100)) if round(self.counter/(self.all/100)) > 0 else 1
                # Костыль если 0 секунд прошло, а уже есть что выводить
                time_now = int(time.time()) - self.start_time if int(time.time()) - self.start_time > 0 else 1
                time_left = round((100-percents)*(time_now/percents))

                print "({0}/{1}/{2}%) | {3} | {4} | {5} o/s".format(
                    nformat(self.counter),
                    nformat(self.all),
                    round(self.counter/(self.all/100), 2),
                    secs_to_text(time_now),
                    secs_to_text(time_left),
                    round((self.counter - self.last_point_count) / (int(time.time()) - self.last_point_time), 2) #round(self.counter/time_now, 2)
                )
                self.last_point_count = self.counter
                self.last_point_time = int(time.time())

        sys.stdout.flush()

        return self

