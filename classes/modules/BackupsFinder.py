# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Module for find backups
"""

import time
import os
from urlparse import urlparse

from libs.common import file_to_list, file_put_contents
from classes.FileGenerator import FileGenerator
from classes.Registry import Registry
from classes.models.HostsModel import HostsModel
from classes.models.UrlsModel import UrlsModel
from classes.models.RequestsModel import RequestsModel
from classes.kernel.WSCounter import WSCounter
from classes.kernel.WSOption import WSOption
from classes.kernel.WSModule import WSModule
from classes.jobs.BackupsFinderJob import BackupsFinderJob
from classes.threads.BackupsFinderThread import BackupsFinderThread
from classes.threads.SBackupsFinderThread import SBackupsFinderThread

class BackupsFinder(WSModule):
    """ Module for find backups """
    model = None
    mode = 'dict'
    log_path = '/dev/null'
    options = {}
    time_count = True
    logger_enable = True
    logger_name = 'backups'
    logger_have_items = True
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
        },
    }

    def validate_main(self):
        """ Method for validate user params """
        super(BackupsFinder, self).validate_main()

    def build_objects(self, host):
        """ Get known urls and build links for check """
        urls = UrlsModel().list_by_host_name(Registry().get('pData')['id'], host)

        links = []
        for url in urls:
            links.append(urlparse(url['url']).path)
        links = list(set(links))

        dirs_exts = file_to_list(Registry().get('wr_path') + "/bases/bf-dirs.txt")
        files_exts = file_to_list(Registry().get('wr_path') + "/bases/bf-files.txt")
        ignore_exts = map(str.strip, map(str, Registry().get('config')['backups']['ignore_exts'].split(',')))

        result = []
        for link in links:
            if link == '/':
                continue
            if link[-1:] == '/':
                link = link.split("/")
                del link[-1]
                last = link[-1]
                del link[-1]

                for dir_ext in dirs_exts:
                    tmp = dir_ext.replace('|name|', last).strip()
                    tmp = "/".join(link) + "/" + tmp
                    result.append(tmp if tmp[0] == '/' else "/" + tmp)
            else:
                ext = link.split(".")[-1]
                if ext in ignore_exts:
                    continue

                link = link.split("/")
                last = link[-1:][0]
                del link[-1:]

                for file_ext in files_exts:
                    tmp = file_ext.replace('|name|', last).strip()
                    tmp = "/".join(link) + "/" + tmp
                    result.append(tmp if tmp[0] == '/' else "/" + tmp)

        return result

    def scan_action(self):
        """ Scan action """
        self.enable_logger()
        self.validate_main()
        self.pre_start_inf()

        if self.options['proxies'].value:
            Registry().get('proxies').load(self.options['proxies'].value)

        result = []

        if os.path.exists('/tmp/bf-urls.txt'):
            os.remove('/tmp/bf-urls.txt')

        urls = self.build_objects(self.options['host'].value)
        for url in urls:
            file_put_contents('/tmp/bf-urls.txt', url + "\n", True)
        q = BackupsFinderJob()

        generator = FileGenerator('/tmp/bf-urls.txt')
        q.set_generator(generator)
        self.logger.log("Loaded {0} variants.".format(generator.lines_count))

        counter = WSCounter(5, 300, generator.lines_count)

        w_thrds = []
        for _ in range(int(self.options['threads'].value)):
            if self.options['selenium'].value:
                worker = SBackupsFinderThread(
                    q,
                    self.options['host'].value,
                    self.options['protocol'].value.lower(),
                    self.options['method'].value.lower(),
                    self.options['not-found-re'].value,
                    self.options['delay'].value,
                    self.options['ddos-detect-phrase'].value,
                    self.options['ddos-human-action'].value,
                    self.options['browser-recreate-re'].value,
                    counter,
                    result
                )
            else:
                worker = BackupsFinderThread(
                    q,
                    self.options['host'].value,
                    self.options['protocol'].value.lower(),
                    self.options['method'].value.lower(),
                    self.options['not-found-re'].value,
                    self.options['not-found-codes'].value.lower(),
                    self.options['delay'].value,
                    counter,
                    result
                )
            worker.setDaemon(True)
            worker.start()
            w_thrds.append(worker)

            time.sleep(1)

        timeout_threads_count = 0
        while len(w_thrds):
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
                            worker = SBackupsFinderThread(
                                q,
                                self.options['host'].value,
                                self.options['protocol'].value.lower(),
                                self.options['method'].value.lower(),
                                self.options['not-found-re'].value,
                                self.options['delay'].value,
                                self.options['ddos-detect-phrase'].value,
                                self.options['ddos-human-action'].value,
                                self.options['browser-recreate-re'].value,
                                counter,
                                result
                            )
                        else:
                            worker = BackupsFinderThread(
                                q,
                                self.options['host'].value,
                                self.options['protocol'].value.lower(),
                                self.options['method'].value.lower(),
                                self.options['not-found-re'].value,
                                self.options['not-found-codes'].value.lower(),
                                self.options['delay'].value,
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

        if result:
            print "\n",
            for item in result:
                print item
            self.logger.log("\nPut found into DB...")

        Requests = RequestsModel()
        Hosts = HostsModel()
        project_id = Registry().get('pData')['id']
        host_id = Hosts.get_id_by_name(project_id, self.options['host'].value)
        added = 0
        for backup in result:
            _id = Requests.add(
                project_id, host_id, backup, "", {}, self.options['method'].value,
                self.options['protocol'].value.lower(), 'backups', 'May be important backup'
            )
            added += 1 if _id else 0

        self.logger.log("Found backups: {0}, new: {1}".format(len(result), added))
        self.logger.log(str(result), _print=False)
        self.done = True
