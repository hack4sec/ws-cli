# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Alexey Meshcheryakov <tank1st99@gmail.com>

Kernel class of modules
"""

import re
import os

from classes.models.HostsModel import HostsModel
from classes.kernel.WSException import WSException
from classes.Registry import Registry


class WSModule(object):
    """ Kernel class of modules """
    log_path = None
    log_width = 60
    description = "module description"
    result = None
    done = False
    options = []
    time_count = False
    logger = None
    logger_enable = False
    options_sets = {}
    action = None

    def __init__(self, kernel):
        self.kernel = kernel
        if self.log_path is None:
            raise WSException('Module must have log path!')

    def enable_logger(self):
        """ Turn on logger """
        self.logger = Registry().get('logger')

    def pre_start_inf(self):
        """ Show options values before work start """
        log_str = ""
        log_str += "---------------------------------\n"
        for option in self.options:
            log_str += "Option '{0}': {1}\n".format(option, self.options[option].value)
        log_str += "---------------------------------"
        print log_str

        if int(Registry().get('config')['main']['confirm']):
            tmp = raw_input("Do you have continue? [Y/n]")
            if len(tmp.strip()) and tmp.lower() != 'y':
                print "Aborted..."
                exit(0)

        self.logger.log(log_str + '\n', new_str=False, _print=False)

    def run(self, action):
        """ Run module """
        getattr(self, action + "_action")()

    def help(self):
        """ Display module help """
        pass

    def finished(self):
        """ Is module finished? """
        return self.done

    def prepare(self, action):
        """ Prepare module for work """
        if action not in self.options_sets:
            raise WSException("Action '{0}' not exists! See help for actions list of this module.".format(action))
        self.options = self.options_sets[action]
        self.action = action

    def validate_main(self):
        """ Common user params validate functions """
        options = self.options_sets[self.action].keys()

        if 'selenium' in self.options.keys() and self.options['selenium'].value:
            if 'not-found-re' in options and not self.options['not-found-re'].value:
                raise WSException("Selenium enabled, module need a not found phrase (--not-found-re) for work!")

            if int(self.options['threads'].value) > int(Registry().get('config')['selenium']['max_threads']):
                raise WSException(
                    "Selenium enabled, very many threads value ({0}), see docs.".format(self.options['threads'].value)
                )

        if 'protocol' in self.options.keys() and self.options['protocol'].value.lower() not in ['http', 'https']:
            raise WSException(
                "Protocol param must be 'http' or 'https', but have value '{0}' !".
                format(self.options['protocol'].value)
            )

        if 'method' in self.options.keys() and self.options['method'].value.lower() not in ['head', 'get', 'post']:
            raise WSException(
                "Method param must be only 'head', 'get' or 'post', but have value '{0}' !".
                format(self.options['method'].value)
            )

        if 'not-found-codes' in self.options.keys() and len(self.options['not-found-codes'].value):
            for code in self.options['not-found-codes'].value.strip().split(","):
                if len(code.strip()) and not re.match(r'^(\d+)$', code.strip()):
                    raise WSException(
                        "Not-found code must be digital, but it is '{0}'".
                        format(code.strip())
                    )

        if 'retest-codes' in self.options.keys() and len(self.options['retest-codes'].value):
            for code in self.options['retest-codes'].value.strip().split(","):
                if len(code.strip()) and not re.match(r'^(\d+)$', code.strip()):
                    raise WSException(
                        "Retest code must be digital, but it is '{0}'".
                        format(code.strip())
                    )

        if 'proxies' in self.options.keys() and len(self.options['proxies'].value) and \
                not os.path.exists(self.options['proxies'].value):
            raise WSException(
                "Proxy list not found: '{0}'".
                format(self.options['proxies'].value)
            )

        if 'not-found-re' in self.options.keys() and len(self.options['not-found-re'].value):
            try:
                re.compile(self.options['not-found-re'].value)
            except re.error:
                raise WSException(
                    "Invalid regex: '{0}'".
                    format(self.options['not-found-re'].value)
                )

        if 'browser-recreate-re' in self.options.keys() and len(self.options['browser-recreate-re'].value):
            try:
                re.compile(self.options['browser-recreate-re'].value)
            except re.error:
                raise WSException(
                    "Invalid regex: '{0}'".
                    format(self.options['browser-recreate-re'].value)
                )

        if 'host' in self.options.keys() and \
                not HostsModel().exists(Registry().get('pData')['id'], self.options['host'].value):
            raise WSException("Host '{0}' not found in this project!".format(self.options['host'].value))

        if 'dict' in self.options.keys() and not os.path.exists(self.options['dict'].value):
            raise WSException("Dictionary '{0}' not exists or not readable!".format(self.options['dict'].value))

        if 'delay' in self.options.keys() and self.options['delay'].value != '0':
            if not re.match(r'^(\d+)$', self.options['delay'].value):
                raise WSException(
                    "Delay param must be digital, but it is '{0}'".
                    format(self.options['delay'].value.strip())
                )

        if 'parts' in self.options.keys() and self.options['parts'].value != '0':
            if not re.match(r'^(\d+)$', self.options['parts'].value):
                raise WSException(
                    "Parts param must be digital, but it is '{0}'".
                    format(self.options['parts'].value.strip())
                )

        if 'part' in self.options.keys() and self.options['part'].value != '0':
            if not re.match(r'^(\d+)$', self.options['part'].value):
                raise WSException(
                    "Part param must be digital, but it is '{0}'".
                    format(self.options['part'].value.strip())
                )

        if 'parts' in self.options.keys() and self.options['parts'].value != '0':
            if self.options['part'].value == '0':
                raise WSException(
                    "If you use '--parts' param, you must specify '--part'"
                )
            if int(self.options['part'].value) > int(self.options['parts'].value):
                raise WSException(
                    "Number of part ({0}) more than parts count ({1})".
                    format(self.options['part'].value.strip(), self.options['parts'].value.strip())
                )

        if 'part' in self.options.keys() and self.options['part'].value != '0':
            if self.options['parts'].value == '0':
                raise WSException(
                    "If you use '--part' param, you must specify '--parts'"
                )