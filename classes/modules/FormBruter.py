# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class of FormBruter module
"""

import time
import os

from classes.Registry import Registry
from classes.FileGenerator import FileGenerator
from classes.jobs.FormBruterJob import FormBruterJob
from classes.models.HostsModel import HostsModel
from classes.kernel.WSModule import WSModule
from classes.kernel.WSException import WSException
from classes.kernel.WSCounter import WSCounter
from classes.kernel.WSOption import WSOption
from classes.threads.FormBruterThread import FormBruterThread
from classes.threads.SFormBruterThread import  SFormBruterThread


class FormBruter(WSModule):
    """ Class of FormBruter module """
    model = None
    mode = 'dict'
    log_path = '/dev/null'
    logger_enable = True
    logger_name = 'form-bruter'
    logger_have_items = True
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
                "Traget host for brute",
                "",
                True,
                ['--host']
            ),
            "url": WSOption(
                "url",
                "Traget url for brute",
                "",
                True,
                ['--url']
            ),
            "protocol": WSOption(
                "protocol",
                "Protocol http or https (default - http)",
                "http",
                False,
                ['--protocol']
            ),
            "false-phrase": WSOption(
                "false-phrase",
                "Phrase for detect false answer (auth is wrong)",
                "",
                False,
                ['--false-phrase']
            ),
            "retest-codes": WSOption(
                "retest-codes",
                "Custom codes for re-test object after 5 sec",
                "",
                False,
                ['--retest-codes']
            ),
            "true-phrase": WSOption(
                "true-phrase",
                "Phrase for detect true answer (auth is good)",
                "",
                False,
                ['--true-phrase']
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
            #"reload-form-page": WSOption(
            #    "reload-form-page",
            #    "Reload page with form before every auth request",
            #    "0",
            #    False,
            #    ['--reload-form-page']
            #),
            "browser-recreate-phrase": WSOption(
                "browser-recreate-phrase",
                "Phrase for recreate browser with new proxy",
                "",
                False,
                ['--browser-recreate-phrase']
            ),
            "proxies": WSOption(
                "proxies",
                "File with list of proxies",
                "",
                False,
                ['--proxies']
            ),
            "confstr": WSOption(
                "confstr",
                "String with bruter config",
                "",
                False,
                ['--confstr']
            ),
            "conffile": WSOption(
                "conffile",
                "File with bruter config (selenium)",
                "",
                False,
                ['--conffile']
            ),
            "first-stop": WSOption(
                "first-stop",
                "Stop after first password found",
                "0",
                False,
                ['--first-stop']
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
            "dict": WSOption(
                "dict",
                "Dictionary for work",
                "",
                True,
                ['--dict']
            ),
            "login": WSOption(
                "login",
                "Target login",
                "",
                True,
                ['--login']
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

    def validate_main(self):
        """ Check users params """
        super(FormBruter, self).validate_main()

        if self.options['url'].value[0] != '/':
            raise WSException("URL must start from root (/)")

        if self.options['selenium'].value:
            if not len(self.options['conffile'].value.strip()):
                raise WSException(
                    "You must specify param --conffile"
                )

            if not os.path.exists(self.options['conffile'].value):
                raise WSException(
                    "Config file '{0}' not exists or not readable!"
                    .format(self.options['conffile'].value)
                )

        else:
            if not len(self.options['confstr'].value.strip()):
                raise WSException(
                    "You must specify param --confstr"
                )
            if not self.options['confstr'].value.count("^USER^"):
                raise WSException(
                    "--confstr must have a ^USER^ fragment"
                )

            if not self.options['confstr'].value.count("^PASS^"):
                raise WSException(
                    "--confstr must have a ^PASS^ fragment"
                )

        if not len(self.options['true-phrase'].value) and not len(self.options['false-phrase'].value):
            raise WSException(
                "You must specify --false-phrase param or --true-phrase param!"
            )


    def load_objects(self, queue):
        """ Prepare work objects """
        generator = FileGenerator(
            self.options['dict'].value,
            int(self.options['parts'].value),
            int(self.options['part'].value)
        )
        queue.set_generator(generator)
        return {'all': generator.lines_count, 'start': generator.first_border, 'end': generator.second_border}

    def brute_action(self):
        """ Brute action of module """
        self.enable_logger()
        self.validate_main()
        self.pre_start_inf()

        if self.options['proxies'].value:
            Registry().get('proxies').load(self.options['proxies'].value)

        result = []

        q = FormBruterJob()
        loaded = self.load_objects(q)

        self.logger.log(
            "Loaded {0} words ({1}-{2}) from all {3}.".format(
                (loaded['end'] - loaded['start']), loaded['start'], loaded['end'], loaded['all'])
            if (int(self.options['parts'].value) and int(self.options['part'].value)) else
            "Loaded {0} words from source.".format(loaded['all'])
        )

        counter = WSCounter(5, 300, loaded['all'] if not loaded['end'] else loaded['end']-loaded['start'])

        w_thrds = []
        pass_found = False
        for _ in range(int(self.options['threads'].value)):
            if self.options['selenium'].value:
                worker = SFormBruterThread(
                    q,
                    self.options['protocol'].value,
                    self.options['host'].value,
                    self.options['url'].value,
                    self.options['false-phrase'].value,
                    self.options['true-phrase'].value,
                    self.options['delay'].value,
                    self.options['ddos-detect-phrase'].value,
                    self.options['ddos-human-action'].value,
                    self.options['browser-recreate-phrase'].value,
                    self.options['conffile'].value,
                    self.options['first-stop'].value.lower(),
                    self.options['login'].value,
                    #self.options['reload-form-page'].value.lower(),
                    pass_found,
                    counter,
                    result
                )
            else:
                worker = FormBruterThread(
                    q,
                    self.options['protocol'].value,
                    self.options['host'].value,
                    self.options['url'].value,
                    self.options['false-phrase'].value,
                    self.options['true-phrase'].value,
                    self.options['retest-codes'].value.lower(),
                    self.options['delay'].value,
                    self.options['confstr'].value,
                    self.options['first-stop'].value.lower(),
                    self.options['login'].value,
                    pass_found,
                    counter,
                    result
                )
            worker.setDaemon(True)
            worker.start()
            w_thrds.append(worker)

            time.sleep(1)

        timeout_threads_count = 0
        while len(w_thrds):
            if Registry().get('proxy_many_died'):
                self.logger.log("Proxy many died, stop scan")

            for worker in w_thrds:
                if Registry().get('proxy_many_died') or Registry().get('positive_limit_stop'):
                    worker.done = True
                    time.sleep(3)

                if worker.done:
                    del w_thrds[w_thrds.index(worker)]

                if int(time.time()) - worker.last_action > int(Registry().get('config')['main']['kill_thread_after_secs']):
                    self.logger.log(
                        "Thread killed by time, resurected {0} times from {1}".format(
                            timeout_threads_count,
                            Registry().get('config')['main']['timeout_threads_resurect_max_count']
                        )
                    )
                    del w_thrds[w_thrds.index(worker)]

                    if timeout_threads_count <= int(Registry().get('config')['main']['timeout_threads_resurect_max_count']):
                        if self.options['selenium'].value:
                            worker = SFormBruterThread(
                                q,
                                self.options['protocol'].value,
                                self.options['host'].value,
                                self.options['url'].value,
                                self.options['false-phrase'].value,
                                self.options['true-phrase'].value,
                                self.options['delay'].value,
                                self.options['ddos-detect-phrase'].value,
                                self.options['ddos-human-action'].value,
                                self.options['browser-recreate-phrase'].value,
                                self.options['conffile'].value,
                                self.options['first-stop'].value.lower(),
                                self.options['login'].value,
                                #self.options['reload-form-page'].value.lower(),
                                pass_found,
                                counter,
                                result
                            )
                        else:
                            worker = FormBruterThread(
                                q,
                                self.options['protocol'].value,
                                self.options['host'].value,
                                self.options['url'].value,
                                self.options['false-phrase'].value,
                                self.options['true-phrase'].value,
                                self.options['retest-codes'].value.lower(),
                                self.options['delay'].value,
                                self.options['confstr'].value,
                                self.options['first-stop'].value.lower(),
                                self.options['login'].value,
                                pass_found,
                                counter,
                                result
                            )
                        worker.setDaemon(True)
                        worker.start()
                        w_thrds.append(worker)

                        timeout_threads_count += 1

            time.sleep(2)

        if Registry().get('positive_limit_stop'):
            self.logger.log("\nMany positive detections. Please, look items logs")
            self.logger.log("Last items:")
            for i in range(1, 5):
                print result[-i]
            exit(0)

        self.logger.log("")
        self.logger.log("Passwords found:")
        for row in result:
            self.logger.log('\t' + row['word'])

        self.done = True
