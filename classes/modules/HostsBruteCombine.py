# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class of module for HostsBrute by Dict+Mask
"""

from classes.kernel.WSOption import WSOption
from classes.Registry import Registry

from classes.modules.HostsBruteModules import HostsBruteModules
from classes.CombineGenerator import CombineGenerator

class HostsBruteCombine(HostsBruteModules):
    """ Class of module for HostsBrute by Dict+Mask """
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
                "Traget host name",
                "",
                True,
                ['--host']
            ),
            "msymbol": WSOption(
                "msymbol",
                "Symbol of mask position in target URL (default {0})"
                .format(Registry().get('config')['main']['standart_msymbol']),
                Registry().get('config')['main']['standart_msymbol'],
                False,
                ['--msymbol']
            ),
            "protocol": WSOption(
                "protocol",
                "Protocol http or https (default - http)",
                "http",
                False,
                ['--protocol']
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
            "false-phrase": WSOption(
                "false-phrase",
                "Phrase for detect 'Host not found' response",
                "",
                True,
                ['--false-phrase']
            ),
            "retest-codes": WSOption(
                "retest-codes",
                "Custom codes for re-test object after 5 sec",
                "",
                False,
                ['--retest-codes']
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
            "proxies": WSOption(
                "proxies",
                "File with list of proxies",
                "",
                False,
                ['--proxies']
            ),
            "template": WSOption(
                "template",
                "Template for brute",
                "",
                True,
                ['--template']
            ),
            "combine-template": WSOption(
                "combine-template",
                "Combine template ",
                "",
                True,
                ['--combine-template']
            ),
        },
    }

    def load_objects(self, queue):
        """ Prepare generator for work """
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
        """ Check users params """
        super(HostsBruteCombine, self).validate_main()

