# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class of module for DAFS by mask
"""
from classes.kernel.WSOption import WSOption
from classes.Registry import Registry
from classes.DictOfMask import DictOfMask
from classes.modules.DafsModules import DafsModules

class DafsMask(DafsModules):
    """ Class of module for DAFS by mask """
    model = None
    mode = 'mask'
    log_path = '/dev/null'
    options = {}
    time_count = True

    options_sets = {
        "scan": {
            "threads": WSOption(
                "threads",
                "Threads count, default 10",
                int(Registry().get('config')['main']['default_threads']),
                False,
                ['--threads']
            ),
            "host": WSOption(
                "host",
                "Traget host for scan",
                "",
                True,
                ['--host']
            ),
            "url": WSOption(
                "url",
                "Target URL (from root)",
                "",
                True,
                ['--url']
            ),
            "msymbol": WSOption(
                "msymbol",
                "Symbol of mask position in target URL (default {0})"
                .format(Registry().get('config')['main']['standart_msymbol']),
                Registry().get('config')['main']['standart_msymbol'],
                False,
                ['--msymbol']
            ),
            "method": WSOption(
                "method",
                "Requests method (default - HEAD)",
                "HEAD",
                False,
                ['--method']
            ),
            "protocol": WSOption(
                "protocol",
                "Protocol http or https (default - http)",
                "http",
                False,
                ['--protocol']
            ),
            "mask": WSOption(
                "mask",
                "Mask for work",
                "",
                True,
                ['--mask']
            ),
            "not-found-re": WSOption(
                "not-found-re",
                "Regex for detect 'Not found' response (404)",
                "",
                False,
                ['--not-found-re']
            ),
            "not-found-codes": WSOption(
                "not-found-codes",
                "Custom codes for detect 'Not found' response (404)",
                "404",
                False,
                ['--not-found-codes']
            ),
            "not-found-size": WSOption(
                "not-found-size",
                "Size in bytes for detect 'Not found' response (404)",
                "-1",
                False,
                ['--not-found-size']
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
            "selenium": WSOption(
                "selenium",
                "Use Selenium for scanning",
                "",
                False,
                ['--selenium']
            ),
            "ddos-detect-phrase": WSOption(
                "ddos-detect-phrase",
                "Phrase for detect DDoS protection",
                "",
                False,
                ['--ddos-detect-phrase']
            ),
            "ddos-human-action": WSOption(
                "ddos-human-action",
                "Phrase for detect human action need",
                "",
                False,
                ['--ddos-human-action']
            ),
            "browser-recreate-re": WSOption(
                "browser-recreate-re",
                "Regex for recreate browser with new proxy",
                "",
                False,
                ['--browser-recreate-re']
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
        },
    }

    def load_objects(self, queue):
        """ Prepare generator for work """
        dom = DictOfMask(self.options['mask'].value, int(self.options['parts'].value), int(self.options['part'].value))

        queue.set_generator(dom)
        return {'all': dom.all_objects_count, 'start': dom.first_border, 'end': dom.second_border}
