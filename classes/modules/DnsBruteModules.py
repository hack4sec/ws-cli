# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Common class for DnsBrute modules
"""

import time
import socket

import dns.query
import dns.message

from classes.Roller import Roller
from classes.Registry import Registry
from classes.kernel.WSCounter import WSCounter
from classes.kernel.WSModule import WSModule
from classes.kernel.WSException import WSException
from classes.models.HostsModel import HostsModel
from classes.models.IpsModel import IpsModel
from classes.jobs.DnsBruteJob import DnsBruteJob
from classes.threads.DnsBruteThread import DnsBruteThread


class DnsBruteModules(WSModule):
    logger_enable = True
    logger_name = 'dns'
    logger_have_items = False
    """ Common class for DnsBrute modules """
    def validate_main(self):
        """ Check users params """
        if self.options['protocol'].value not in ['tcp', 'udp', 'auto']:
            raise WSException(
                "Protocol mast be 'tcp', 'udp' or 'auto', but it is '{0}'"
                .format(self.options['protocol'].value)
            )

    def load_objects(self, queue):
        """ Method for prepare test objects, here abstract """
        pass

    def brute_action(self):
        """ Action brute of module """
        self.enable_logger()
        self.validate_main()
        self.pre_start_inf()

        q = DnsBruteJob()

        loaded = self.load_objects(q)
        self.logger.log("Loaded {0} words from dict.".format(loaded['all']))

        counter = WSCounter(5, 300, loaded['all'])

        result = []

        w_thrds = []
        DnsRoller = Roller()
        DnsRoller.load_file(Registry().get('wr_path') + '/bases/dns-servers.txt')
        for _ in range(int(self.options['threads'].value)):
            we_need_server = True
            while we_need_server:
                we_need_server = False
                try:
                    next_server = DnsRoller.get()
                    #print "Next DNS " + next_server
                    if self.options['protocol'].value == 'auto':
                        try:
                            dns.query.tcp(dns.message.make_query('test.com', 'A'), next_server, timeout=5)
                            protocol = 'tcp'
                        except socket.error:
                            try:
                                dns.query.udp(dns.message.make_query('test.com', 'A'), next_server, timeout=5)
                                protocol = 'udp'
                            except socket.error:
                                #raise Exception('Can`t detect DNS-server protocol. Check addr.')
                                we_need_server = True #TODO по-человечески сделать
                        #print 'DNS protolol detected automaticaly: ' + protocol
                    else:
                        protocol = self.options['protocol'].value
                except dns.exception.Timeout:
                    self.logger.log("Check server {0}. Don`t work.".format(next_server))
                    we_need_server = True

            worker = DnsBruteThread(
                q,
                self.options['host'].value,
                protocol,
                self.options['msymbol'].value,
                next_server,
                self.options['delay'].value,
                result,
                counter
            )
            worker.setDaemon(True)
            worker.start()
            w_thrds.append(worker)

            time.sleep(1)

        while len(w_thrds):
            for worker in w_thrds:
                if worker.done or Registry().get('positive_limit_stop'):
                    del w_thrds[w_thrds.index(worker)]
            time.sleep(2)

        self.logger.log("\nFound hosts:")
        for host in result:
            self.logger.log("\t{0} (DNS: {1})".format(host['name'], host['dns']))
        self.logger.log("Found IPs:")

        uniq_hosts = []
        for host in result:
            uniq_hosts.append(host['ip'])
        uniq_hosts = list(set(uniq_hosts))

        for host in uniq_hosts:
            self.logger.log("\t" + host)

        if not Registry().get('positive_limit_stop'):
            self.logger.log("Put found hosts into DB...")
            added = self._insert_hosts(result)

            self.logger.log("\nFound {0} hosts, inserted in database (new) - {1}.".format(len(result), added))
        else:
            self.logger.log("Found")

        self.done = True

    def _insert_hosts(self, hosts):
        """ Add found hosts in db """
        pid = Registry().get('pData')['id']

        Hosts = HostsModel()
        Ips = IpsModel()

        added = 0
        for host in hosts:
            ip_id = Ips.get_id_or_add(pid, host['ip'])
            if Hosts.add(pid, ip_id, host['name'], founder='dnsbrute'):
                added += 1

        return added
