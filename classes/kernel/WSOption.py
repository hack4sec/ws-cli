# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Alexey Meshcheryakov <tank1st99@gmail.com>

Kernel class of run args
"""


class WSOption(object):
    """ Kernel class of run args """
    def __init__(self, name, description, value, required, flags, module=None):
        self.name = name
        self.description = description
        self.value = value
        self.required = required
        self.flags = flags
        self.module = module
