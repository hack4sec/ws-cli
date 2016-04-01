# -*- coding: utf-8 -*-
""" Class of roller list (get last element - next first element) """
from libs.common import file_to_list

class Roller(object):
    """ Class of roller list (get last element - next first element) """
    data = []
    current_index = 0

    def load_file(self, file_name):
        """ Method load file in inner list """
        for line in file_to_list(file_name, False):
            if len(line):
                self.data.append(line)

    def get(self):
        """ Method get next list item """
        to_return = self.data[self.current_index]

        if self.current_index == len(self.data)-1:
            self.current_index = 0
        else:
            self.current_index += 1
        return to_return
