# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class of Spider module
"""
import os
import re
import time

from libs.common import parse_split_conf
from classes.Registry import Registry
from classes.SpiderCommon import SpiderCommon
from classes.SpiderResult import SpiderResult
from classes.SpiderRequestsCounter import SpiderRequestsCounter
from classes.models.HostsModel import HostsModel
from classes.kernel.WSModule import WSModule
from classes.kernel.WSException import WSException
from classes.kernel.WSOption import WSOption
from classes.kernel.WSCounter import WSCounter
from classes.threads.SpiderThread import SpiderThread
from classes.threads.SSpiderThread import SSpiderThread
from classes.jobs.SpiderJob import SpiderJob


class SpiderException(Exception):
    """ Class of Spider exceptions """
    pass


class Spider(WSModule):
    """ Class of Spider module """
    model = None
    log_path = '/dev/null'
    time_count = True
    logger_enable = True
    logger_name = 'spider'
    logger_have_items = False
    options_sets = {
        "scan": {
            "threads": WSOption(
                "threads",
                "Threads count, default 10",
                int(Registry().get('config')['main']['default_threads']),
                False,
                ['--threads']
            ),
            "ignore": WSOption(
                "ignore",
                "ignore regexp",
                "",
                False,
                ['--ignore-re']
            ),
            "only_one": WSOption(
                "only_one",
                "only one",
                "",
                False,
                ['--only-one']
            ),
            "host": WSOption(
                "host",
                "Traget host for scan",
                "",
                True,
                ['--host']
            ),
            "full-new": WSOption(
                "full-new",
                "full new scan",
                "",
                False,
                ['--full-new']
            ),
            "not-found-re": WSOption(
                "not-found-re",
                "Regex for detect 'Not found' response (404)",
                "",
                False,
                ['--not-found-re']
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
            "proxies": WSOption(
                "proxies",
                "File with list of proxies",
                "",
                False,
                ['--proxies']
            ),
            "headers-file": WSOption(
                "headers-file",
                "File with list of HTTP headers",
                "",
                False,
                ['--headers-file']
            ),
        }
    }

    def validate_main(self):
        """ Check users params """
        super(Spider, self).validate_main()

    def _options_to_registry(self):
        if self.options['ignore'].value:
            Registry().set('ignore_regexp', re.compile(self.options['ignore'].value))

        expr = ''
        for ext in Registry().get('config')['spider']['allow_exts'].split(','):
            expr += r'\.' + ext.strip() + '$|'
        expr = expr.rstrip('|')
        Registry().set('allow_regexp', re.compile(expr, re.I))

        if self.options['only_one'].value:
            tmp = self.options['only_one'].value.split("||")
            if len(tmp):
                only_one = []
                for regex in tmp:
                    only_one.append({'regex': regex, 'block': False})
                Registry().set('only_one', only_one)

        denied_schemes = parse_split_conf(Registry().get('config')['spider']['denied_schemes'])
        Registry().set('denied_schemes', denied_schemes)
        Registry().get('http').set_allowed_types(
            parse_split_conf(Registry().get('config')['spider']['scan_content_types'])
        )
        Registry().get('http').set_denied_types(
            parse_split_conf(Registry().get('config')['spider']['noscan_content_types'])
        )

    def scan_action(self):
        """ Scan action of module """
        self.enable_logger()
        self.validate_main()
        self.pre_start_inf()

        if self.options['proxies'].value:
            Registry().get('proxies').load(self.options['proxies'].value)

        SpiderCommon.clear_old_data(self.options['host'].value)

        self.result = SpiderResult()
        self._options_to_registry()

        if self.options['full-new'].value:
            SpiderCommon.make_full_new_scan(Registry().get('pData')['id'])

        SpiderCommon.prepare_first_pages(self.options['host'].value)

        if not os.path.exists(Registry().get('data_path') + self.options['host'].value):
            os.mkdir(Registry().get('data_path') + self.options['host'].value)
            os.chmod(Registry().get('data_path') + self.options['host'].value, 0o777)

        job = SpiderJob()
        src = SpiderRequestsCounter(int(Registry().get('config')['spider']['requests_limit']))
        counter = WSCounter(5, 300, 0)

        workers = []
        for _ in range(int(self.options['threads'].value)):
            if self.options['selenium'].value:
                worker = SSpiderThread(
                    job,
                    self.options['host'].value,
                    src,
                    self.options['not-found-re'].value,
                    self.options['delay'].value,
                    self.options['ddos-detect-phrase'].value,
                    self.options['ddos-human-action'].value,
                    self.options['browser-recreate-re'].value,
                    counter
                )
            else:
                worker = SpiderThread(
                    job,
                    self.options['host'].value,
                    src,
                    self.options['delay'].value,
                    counter
                )
            worker.setDaemon(True)
            workers.append(worker)
            time.sleep(1)
        self.kernel.create_threads(workers)

        while not self.kernel.finished():
            time.sleep(2)

        if int(Registry().get('config')['main']['put_data_into_db']):
            self.logger.log("\nPut results into DB...")
            SpiderCommon.links_in_database(
                Registry().get('pData')['id'],
                self.options['host'].value
            )
        else:
            self.logger.log("\nResults NOT put into DB")

        self.logger.log("\nTotal links count: " + str(Registry().get('mongo').spider_urls.count()))
        self.logger.log(str(self.result))

    def help(self):
        """ Help func """
        return "Module Spider ver 1.0"

    def finished(self):
        """ Is module finished? """
        return self.kernel.finished()

