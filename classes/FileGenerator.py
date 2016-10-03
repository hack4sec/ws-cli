# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class for file generator
"""


class FileGenerator(object):
    """ Class for file generator """
    _fh = None
    lines_count = 0
    current_counter = 0
    first_border = 0
    second_border = 0

    def __init__(self, _file, parts=0, part=0):
        self._fh = open(_file)

        tmp_fh = open(_file)
        tmp_data_last = ''
        tmp_data = ''
        while True:
            tmp_data_last = str(tmp_data)
            tmp_data = tmp_fh.read(2048)
            if not tmp_data:
                if len(tmp_data_last) and tmp_data_last[-1] != '\n':
                    self.lines_count += 1
                break
            self.lines_count += tmp_data.count("\n")

        if parts and part:
            one_part_count = int(self.lines_count/parts)
            self.first_border = one_part_count * (part - 1)
            self.second_border = one_part_count * part

            if self.first_border:
                for _ in range(0, self.first_border-1):
                    self._fh.readline()
                    self.current_counter += 1


    def get(self):
        """ Return current file line """
        self.current_counter += 1
        line = self._fh.readline()

        if self.second_border:
            if self.current_counter <= self.first_border:
                return self.get()
            if self.current_counter > self.second_border:
                return None

        return line.strip() if line else None
