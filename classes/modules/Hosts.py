# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class of Hosts module
"""
import socket
import os

from libs.common import validate_host, validate_ip
from classes.Registry import Registry
from classes.kernel.WSModule import WSModule
from classes.kernel.WSOption import WSOption
from classes.kernel.WSException import WSException
from classes.models.IpsModel import IpsModel
from classes.models.HostsModel import HostsModel

class Hosts(WSModule):
    """ Class of Hosts module """
    model = None
    log_path = '/dev/null'
    options = {}
    options_sets = {
        "list": {
            "ip": WSOption("ip", "IP for host list", "", False, ['--ip']),
        },
        "delete": {
            "host": WSOption("host", "Host for delete", "", True, ['--host']),
        },
        "add": {
            "host": WSOption("host", "Host for add", "", True, ['--host']),
            "ip": WSOption("ip", "Custom IP for this host", "", False, ['--ip']),
            "descr": WSOption("descr", "Description of host", "", False, ['--descr'])
        },
        "addlist": {
            "file": WSOption("file", "File with hosts for add", "", True, ['--file']),
            "ip": WSOption("ip", "Custom IP for this hosts", "", False, ['--ip']),
            "descr": WSOption("descr", "Description of hosts", "", False, ['--descr'])
        },
    }

    def __init__(self, kernel):
        WSModule.__init__(self, kernel)
        self.model = HostsModel()

    def validate_main(self):
        """ Check users params """
        if 'host' in self.options and not \
                (validate_host(self.options['host'].value) or validate_ip(self.options['host'].value)):
            raise WSException("'{0}' is not valid host name or ip!".format(self.options['host'].value))
        if 'ip' in self.options and self.options['ip'].value:
            if not validate_ip(self.options['ip'].value):
                raise WSException("IP '{0}' is not valid ip-address!".format(self.options['ip'].value))
        if 'list' in self.options and self.options['file'].value:
            if not os.path.exists(self.options['file'].value):
                raise WSException("File {0} not exists or not readable".format(self.options['file'].value))

    def run(self, action):
        """ Method of run the module """
        WSModule.run(self, action)
        self.done = True

    def add_action(self):
        """ Action add of module """
        self.validate_main()
        self._add_host(self.options['host'].value, self.options['ip'].value, self.options['descr'].value)

    def addlist_action(self):
        """ Action add of module """
        self.validate_main()

        fh = open(self.options['file'].value, 'r')
        for line in fh:
            line = line.strip()
            if len(line):
                self._add_host(line, self.options['ip'].value, self.options['descr'].value)
        fh.close()

    def _add_host(self, name, ip='', descr=""):
        pData = Registry().get('pData')

        if ip == '':
            try:
                ip = socket.gethostbyname(name)
                print " IP for host '{0}' is '{1}'".format(name, ip)
            except socket.gaierror:
                raise WSException("Can`t lookup hostname '{0}'. Check it or set ip-address in --ip param!".format(name))

        IPs = IpsModel()
        ip_exists = IPs.exists(pData['id'], ip)
        ip_id = IPs.get_id_or_add(pData['id'], ip)
        if not ip_exists:
            print " IP '{0}' was automatically added to project '{1}'".format(ip, pData['name'])

        if self.model.exists(pData['id'], name):
            raise WSException("Host '{0}' already exists in project '{1}'!".format(name, pData['name']))

        self.model.add(pData['id'], ip_id, name, descr)
        print " Host '{0}' successfully added to project '{1}' with IP '{2}' ! ".format(
            name, pData['name'], ip
        )

    def list_action(self):
        """ Action list of module """
        if self.options['ip'].value:
            print "{0:=^51}".format("")
            print "|{0: ^49}|".format("Hosts for IP '{0}'".format(self.options['ip'].value))
            print "{0:=^51}".format("")
            print "| {0: ^23}| {1: ^23}|".format('Title', 'Description')
            print "{0:=^51}".format("")
            for host in self.model.list(Registry().get('pData')['id'], self.options['ip'].value):
                print "| {0: <23}| {1: <23}|".format(host['name'], host['descr'])
            print "{0:=^51}".format("")
        else:
            print "{0:=^76}".format("")
            print "|{0: ^74}|".format("All host for project '{0}'".format(Registry().get('pData')['name']))
            print "{0:=^76}".format("")
            print "| {0: ^23}| {1: ^23}| {2: ^23}|".format('Title', 'Description', 'IP')
            print "{0:=^76}".format("")
            for host in self.model.list_without_ip(Registry().get('pData')['id']):
                print "| {0: <23}| {1: <23}| {2: <23}|".format(host['name'], host['descr'], host['ip'])
            print "{0:=^76}".format("")

    def delete_action(self):
        """ Delete action of module """
        self.validate_main()

        name = self.options['host'].value

        if not self.model.exists(Registry().get('pData')['id'], name):
            raise WSException("Host '{0}' not exists in this project!".format(name))

        answer = raw_input("You really want to delete host '{0}' [y/n]? ".format(name))
        if answer.lower() == 'y':
            self.model.delete(Registry().get('pData')['id'], name)
            print "Host '{0}' successfully deleted.".format(name)
        else:
            print "Host '{0}' not deleted.".format(name)
