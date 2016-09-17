# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Alexey Meshcheryakov <tank1st99@gmail.com>

Kernel class of WS exceptions
"""


class WSException(Exception):
    """ Kernel class of WS exceptions """

    def __init__(self, error_message=""):
        super(WSException, self).__init__(error_message)
        self.error_message = error_message

    def __str__(self):
        """ How show as str? """
        return "ERROR: " + self.error_message
