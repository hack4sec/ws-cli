# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class for generate and work with masks
"""

import re
import time


class DictOfMask(object):
    """ Class for generate and work with masks """
    mask = None
    masks = None
    mask_num = 0
    mask_symbol_num = 1
    mask_symbol_in_symbol_num = 0
    masks_keys = []
    done = False
    new_masks = {}
    symbols_points = {}
    work_mask = None
    all_objects_count = 0
    current_counter = 0
    first_border = 0
    second_border = 0

    def __init__(self, mask, parts=0, part=0):
        self.mask = mask
        self.masks = self.generate_masks(self.mask)
        self._prepare()

        if parts and part:
            one_part_count = int(self.all_objects_count/parts)
            self.first_border = one_part_count * (part - 1)
            self.second_border = one_part_count * part

            if self.first_border:
                for _ in range(0, self.first_border-1):
                    self._get()
                    self.current_counter += 1


    def keys_in_str(self, _str, keys):
        """ Are the key-symbols (?d,etc) in this str? """
        for key in keys:
            if _str.find(key) != -1:
                return True
        return False

    def generate_masks(self, mask):
        """
        Method get raw mask in human view and return mask in work view (for WS).
        For example: ?l?d,1,3 = [{1: 'a...9'}, {1: 'a...9', 2: 'a...9'}, {1: 'a...9', 2: 'a...9', 3: 'a...9'}]
        For example: ?1=?l?d ?1?1?1 = [{1: 'a...9', 2: 'a...9', 3: 'a...9'}]
        For example: ?l?l = [{1: 'a...z', 2: 'a...z'}]
        :param mask: mask in raw view
        :return: list of work masks
        """
        charsets = {
            '?d': r'0123456789',
            '?l': r'abcdefghijklmnopqrstuvwxyz',
            '?u': r'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            '?s': r'\!@#$%^&*()[]{}`~-_=+|;:\'",.<>/?'
        }

        masks = {}
        if re.match(r'^.*,\d+,\d+$', mask):
            end_limit = int(mask[mask.rfind(',')+1:])
            tmp = mask[:mask.rfind(',')]
            start_limit = int(tmp[tmp.rfind(',')+1:])
            mask = tmp[:tmp.rfind(',')]
            for i in range(start_limit, end_limit+1):
                mask_name = mask + ',' + str(start_limit) + ',' + str(i)
                self.masks_keys.append(mask_name)
                masks[mask_name] = {}
                for c in range(i):
                    masks[mask_name][c+1] = self.raw_mask(mask, charsets)
        else:
            masks[mask] = {}
            mask_symbols = self.get_symbols(mask)
            for s in mask_symbols:
                masks[mask][s+1] = self.raw_mask(mask_symbols[s], charsets)

        for mask in masks:
            mask_object_count = 1
            for x in masks[mask]:
                #mask_object_count += pow(len(masks[mask][x]), x)
                mask_object_count *= len(masks[mask][x])
            self.all_objects_count += mask_object_count

        return masks

    def raw_mask(self, mask, charsets):
        """ Method replace a mask-template for it charset (?l = a...z)  """
        return_mask = []

        while self.keys_in_str(mask, charsets.keys()):
            for charset in charsets:
                mask = mask.replace(charset, charsets[charset])

        for s in mask:
            return_mask.append(s)

        return return_mask

    def get_symbols(self, mask):
        """ Method return a dict of symbols from mask (?lt = {1: '?l', 2: 't'}) """
        symbols = {}
        counter = 0
        while True:
            try:
                symbol = mask[0]
                if symbol == '?':
                    symbols[counter] = symbol + mask[1]
                    mask = mask[2:]
                else:
                    symbols[counter] = symbol
                    mask = mask[1:]
                counter += 1
            except IndexError:
                break

        return symbols

    def dict(self):
        """ Make a list from mask (why it named so?). ?l = ['a', 'b', 'c'] """
        masks = self.generate_masks(self.mask)
        dicts = []
        for mask in masks:
            _dict = []
            for symbol_num in masks[mask]:
                tmp = []
                for symbol in masks[mask][symbol_num]:
                    if len(_dict):
                        for word in _dict:
                            tmp.append(word + symbol)
                    else:
                        tmp.append(symbol)
                _dict = tmp
            dicts.extend(_dict)
        return dicts

    def _prepare(self):
        """ Internal method for build self.symbols_points from current mask """
        self.work_mask = self.masks.keys()[self.mask_num]
        self.symbols_points = {}
        for n in self.masks[self.work_mask].keys():
            self.symbols_points[n] = 0

    def _up_last_point(self):
        """ Method up internal point counter. It`s need for generator. """
        last_point = max(self.symbols_points.keys())
        self.symbols_points[last_point] += 1

        if self.symbols_points[last_point] > len(self.masks[self.work_mask][last_point]) - 1:
            self.calculate_points()

    def calculate_points(self):
        """ Method calculate next masks and symbols position (generator function) """
        changed = True
        while changed:
            changed = False
            for i in range(1, max(self.symbols_points.keys())+1):
                if i not in self.symbols_points.keys():
                    break

                if self.symbols_points[i] > len(self.masks[self.work_mask][i]) - 1:
                    self.symbols_points[i] = 0
                    try:
                        self.symbols_points[i-1] += 1
                    except KeyError:
                        if self.mask_num == len(self.masks)-1:
                            self.done = True
                            return

                        self.mask_num += 1
                        self._prepare()

                    changed = True

    def get(self):
        """ Get current word from mask set (aa, ab, ac...)"""
        self.current_counter += 1

        if self.done:
            return None

        if self.second_border:
            if self.current_counter <= self.first_border:
                return self.get()
            if self.current_counter > self.second_border:
                return None

        to_return = self._get()

        return ''.join(to_return)

    def _get(self):
        """ Get symbol for every mask position and return list of it """
        to_return = []
        for point in self.symbols_points:
            try:
                to_return.append(self.masks[self.work_mask][point][self.symbols_points[point]])
            except IndexError:
                time.sleep(0.1)
                return self._get()

        self._up_last_point()
        return to_return
