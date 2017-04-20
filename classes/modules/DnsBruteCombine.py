# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class of WS Module for DNS Brute by dict+mask
"""

import os

from classes.kernel.WSOption import WSOption
from classes.kernel.WSException import WSException
from classes.modules.DnsBruteModules import DnsBruteModules
from classes.Registry import Registry
from classes.CombineGenerator import CombineGenerator

class DnsBruteCombine(DnsBruteModules):
    """ Class of WS Module for DNS Brute by dict+mask """
    model = None
    mode = 'dict'
    log_path = '/dev/null'
    options = {}
    time_count = True
    options_sets = {
        "brute": {
            "threads": WSOption(
                "threads",
                "Threads count, default 10",
                int(Registry().get('config')['main']['default_threads']),
                False,
                ['--threads']
            ),
            "host": WSOption(
                "host",
                "Target hostname",
                "",
                True,
                ['--host']
            ),
            "protocol": WSOption(
                "protocol",
                "TCP or UDP connection to DNS server (default - auto)",
                "auto",
                False,
                ['--protocol']
            ),
            "msymbol": WSOption(
                "msymbol",
                "Symbol of mask position in target hostname (default {0})"
                .format(Registry().get('config')['main']['standart_msymbol']),
                Registry().get('config')['main']['standart_msymbol'],
                False,
                ['--msymbol']
            ),
            "dict": WSOption(
                "dict",
                "Dictionary for work",
                "",
                True,
                ['--dict']
            ),
            "mask": WSOption(
                "mask",
                "Mask for work",
                "",
                True,
                ['--mask']
            ),
            "combine-template": WSOption(
                "combine-template",
                "Template for combine",
                "",
                True,
                ['--combine-template']
            ),
            "template": WSOption(
                "template",
                "Template for brute",
                "",
                True,
                ['--template']
            ),
            "delay": WSOption(
                "delay",
                "Deley for every thread between requests (secs)",
                "0",
                False,
                ['--delay']
            ),
            "parts": WSOption(
                "parts",
                "How many parts will be create from current source (dict/mask)",
                "0",
                False,
                ['--parts']
            ),
            "part": WSOption(
                "part",
                "Number of part for use from --parts",
                "0",
                False,
                ['--part']
            ),
            "ignore-ip": WSOption(
                "ignore-ip",
                "This IP-address must be ignore in positive detections",
                "",
                False,
                ['--ignore-ip']
            ),
            "http-not-found-re": WSOption(
                "http-not-found-re",
                "Regex for detect 'Not found' response by domain name",
                "",
                False,
                ['--http-not-found-re']
            ),
            "headers-file": WSOption(
                "headers-file",
                "File with list of HTTP headers",
                "",
                False,
                ['--headers-file']
            ),
        },
    }

    def load_objects(self, queue):
        """ Make generator with objects to check """
        generator = CombineGenerator(
            self.options['mask'].value,
            self.options['dict'].value,
            int(self.options['parts'].value),
            int(self.options['part'].value),
            self.options['combine-template'].value
        )
        queue.set_generator(generator)
        return {'all': generator.lines_count, 'start': generator.first_border, 'end': generator.second_border}

    def validate_main(self):
        """ Method for validate user params """
        super(DnsBruteCombine, self).validate_main()

