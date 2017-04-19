# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class of FuzzerHeaders module
"""

import time
from urlparse import urlparse

from classes.Registry import Registry
from classes.jobs.FuzzerHeadersJob import FuzzerHeadersJob
from classes.kernel.WSCounter import WSCounter
from classes.kernel.WSOption import WSOption
from classes.kernel.WSModule import WSModule
from classes.models.HostsModel import HostsModel
from classes.models.UrlsModel import UrlsModel
from classes.models.RequestsModel import RequestsModel
from classes.threads.FuzzerHeadersThread import FuzzerHeadersThread


class FuzzerHeaders(WSModule):
    """ Class of FuzzerHeaders module """
    model = None
    log_path = '/dev/null'
    options = {}
    time_count = True
    logger_enable = True
    logger_name = 'fuzzer-headers'
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
            "host": WSOption(
                "host",
                "Traget host for scan",
                "",
                True,
                ['--host']
            ),
            "method": WSOption(
                "method",
                "Requests method (default - GET)",
                "GET",
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
            "delay": WSOption(
                "delay",
                "Deley for every thread between requests (secs)",
                "0",
                False,
                ['--delay']
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

    def validate_main(self):
        """ Check users params """
        super(FuzzerHeaders, self).validate_main()

    def scan_action(self):
        """ Scan action of module """
        self.enable_logger()
        self.validate_main()
        self.pre_start_inf()

        if self.options['proxies'].value:
            Registry().get('proxies').load(self.options['proxies'].value)

        result = []

        q = FuzzerHeadersJob()
        U = UrlsModel()
        urls = U.list_by_host_name(Registry().get('pData')['id'], self.options['host'].value)
        to_scan = []
        for url in urls:
            to_scan.append(url['url'])
        q.load_dict(to_scan)

        self.logger.log("Loaded {0} variants.".format(len(to_scan)))

        counter = WSCounter(1, 60, len(to_scan))

        w_thrds = []
        for _ in range(int(self.options['threads'].value)):
            worker = FuzzerHeadersThread(
                q,
                self.options['host'].value,
                self.options['protocol'].value.lower(),
                self.options['method'].value.lower(),
                self.options['delay'].value,
                counter,
                result
            )
            worker.setDaemon(True)
            worker.start()
            w_thrds.append(worker)

            time.sleep(1)

        while len(w_thrds):
            for worker in w_thrds:
                if worker.done:
                    del w_thrds[w_thrds.index(worker)]
            time.sleep(2)

        Requests = RequestsModel()
        Hosts = HostsModel()
        project_id = Registry().get('pData')['id']
        host_id = Hosts.get_id_by_name(project_id, self.options['host'].value)
        added = 0
        for fuzz in result:
            self.logger.log("{0} {1}://{2}{3} (Word: {4}, Header: {5})".format(
                self.options['method'].value.upper(),
                self.options['protocol'].value.lower(),
                self.options['host'].value,
                fuzz['url'],
                ", ".join(fuzz['words']),
                fuzz['header']
            ))

            if int(Registry().get('config')['main']['put_data_into_db']):
                _id = Requests.add(
                    project_id,
                    host_id,
                    urlparse(fuzz['url']).path,
                    urlparse(fuzz['url']).query,
                    {fuzz['header']: Registry().get('fuzzer_evil_value')},
                    self.options['method'].value,
                    self.options['protocol'].value.lower(),
                    'fuzzer',
                    'Found word(s): {0}'.format(", ".join(fuzz['words']))
                )
                added += 1 if _id else 0
        self.logger.log("\nAdded {0} new requests in database".format(added))

        self.done = True
