# -*- coding: utf-8 -*-
""" Kernel class of WS exceptions """


class WSException(Exception):
    """ Kernel class of WS exceptions """

    def __init__(self, error_message=""):
        super(WSException, self).__init__(error_message)
        self.error_message = error_message

    def __str__(self):
        """ How show as str? """
        return "ERROR: " + self.error_message
