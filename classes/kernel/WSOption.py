# -*- coding: utf-8 -*-
""" Kernel class of run args """


class WSOption(object):
    """ Kernel class of run args """
    def __init__(self, name, description, value, required, flags, module=None):
        self.name = name
        self.description = description
        self.value = value
        self.required = required
        self.flags = flags
        self.module = module
