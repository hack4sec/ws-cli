# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class of ips module
"""

from libs.common import validate_ip

from classes.Registry import Registry
from classes.kernel.WSModule import WSModule
from classes.kernel.WSOption import WSOption
from classes.kernel.WSException import WSException
from classes.models.IpsModel import IpsModel


class IPs(WSModule):
    """ Class of ips module """
    model = None
    log_path = '/dev/null'
    options = {}
    options_sets = {
        "list": {

        },
        "delete": {
            "ip": WSOption("ip", "IP for delete", "", True, ['--ip']),
        },
        "add": {
            "ip": WSOption("ip", "IP for add", "", True, ['--ip']),
            "descr": WSOption("descr", "Description of IP", "", False, ['--descr'])
        }
    }

    def __init__(self, kernel):
        WSModule.__init__(self, kernel)
        self.model = IpsModel()

    def validate_main(self):
        """ Check users params """
        if not validate_ip(self.options['ip'].value):
            raise WSException("IP '{0}' is not valid ip-address!".format(self.options['ip'].value))


    def add_action(self):
        """ Action add of module """
        self.validate_main()

        pData = Registry().get('pData')
        ip = self.options['ip'].value
        descr = self.options['descr'].value

        if self.model.exists(pData['id'], ip):
            raise WSException("IP '{0}' already exists in project '{1}'!".format(ip, pData['name']))

        self.model.add(pData['id'], ip, descr)
        print " IP '{0}' successfully added to project '{1}' ! ".format(
            ip, pData['name']
        )

    def list_action(self):
        """ Action list of module """
        print "{0:=^51}".format("")
        print "| {0: ^23}| {1: ^23}|".format('IP', 'Description')
        print "{0:=^51}".format("")
        for ip in self.model.list(Registry().get('pData')['id']):
            print "| {0: <23}| {1: <23}|".format(ip['ip'], ip['descr'])
        print "{0:=^51}".format("")

    def delete_action(self):
        """ Delete action of module """
        self.validate_main()

        ip = self.options['ip'].value

        if not self.model.exists(Registry().get('pData')['id'], ip):
            raise WSException("IP '{0}' not exists in this project!".format(ip))

        answer = raw_input("You really want to delete ip '{0}' [y/n]? ".format(ip))
        if answer.lower() == 'y':
            self.model.delete(Registry().get('pData')['id'], ip)
            print "IP '{0}' successfully deleted.".format(ip)
        else:
            print "IP '{0}' not deleted.".format(ip)

    def run(self, action):
        """ Method of run the module """
        WSModule.run(self, action)
        self.done = True

