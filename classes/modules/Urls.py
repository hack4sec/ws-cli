# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class of Urls module
"""
import datetime

from classes.Registry import Registry
from classes.kernel.WSModule import WSModule
from classes.kernel.WSOption import WSOption
from classes.kernel.WSException import WSException
from classes.models.HostsModel import HostsModel
from classes.models.UrlsModel import UrlsModel


class Urls(WSModule):
    """ Class of Urls module """
    model = None
    log_path = '/dev/null'
    options = {}
    options_sets = {
        "list": {
            "host": WSOption("host", "Host for view urls", "", True, ['--host']),
            "like": WSOption("like", "Word for LIKE sql-expression, like %word%.", "", False, ['--like']),
        },
        "export": {
            "host": WSOption("host", "Host for view urls", "", True, ['--host']),
            "like": WSOption("like", "Word for LIKE sql-expression, like %word%.", "", False, ['--like']),
            "without-host": WSOption(
                "without-host",
                "Print host in links (1) or no (0). Default (0).",
                "1",
                False,
                ['--without-host']
            ),
            "protocol": WSOption(
                "protocol",
                "Protocol http or https (default - http)",
                "http",
                False,
                ['--protocol']
            ),
        },
        "delete": {
            "url": WSOption("url", "URL for add", "", True, ['--url']),
            "host": WSOption("host", "Host for add", "", True, ['--host']),
        },
        "add": {
            "url": WSOption("url", "URL for add", "", True, ['--url']),
            "host": WSOption("host", "Host for add", "", True, ['--host']),
            "descr": WSOption("descr", "Description of URL", "", False, ['--descr'])
        }
    }

    def __init__(self, kernel):
        WSModule.__init__(self, kernel)
        self.model = UrlsModel()

    def validate_main(self):
        """ Check users params """
        if not HostsModel().exists(Registry().get('pData')['id'], self.options['host'].value):
            raise WSException("Host '{0}' not found in this project!".format(self.options['host'].value))

        if 'url' in self.options and self.options['url'].value[0] != '/':
            raise WSException("URL must start from the root ('/') !")

    def list_action(self):
        """ Action list of module """
        self.validate_main()

        print "{0:=^111}".format("")
        print "|{0: ^99}|".format("URLs of host '{0}'".format(self.options['host'].value))
        print "{0:=^111}".format("")
        print "| {0: ^23}| {1: ^7}| {2: ^8}| {3: ^23}| {4: ^19}| {5: ^8}| {6: ^8}|".\
              format('URL', 'Code', 'Time', 'Description', 'Added', 'Who', 'Size')
        print "{0:=^111}".format("")

        urls = self.model.list_by_host_name(
            Registry().get('pData')['id'],
            self.options['host'].value,
            self.options['like'].value
        )
        for url in urls:
            print "| {0: <23}| {1: ^7}| {2: <7} | {3: <23}| {4: <19}| {5: ^8}| {6: ^8}|".\
                  format(
                      url['url'],
                      url['code'],
                      str(url['time']) + " sec",
                      url['descr'],
                      datetime.datetime.fromtimestamp(int(url['when_add'])).strftime('%Y-%m-%d %H:%M:%S'),
                      url['who_add'],
                      url['size']
                  )

        print "{0:=^111}".format("")

    def export_action(self):
        """ Action list of module """
        self.validate_main()

        urls = self.model.list_by_host_name(
            Registry().get('pData')['id'],
            self.options['host'].value,
            self.options['like'].value
        )
        for url in urls:
            if not int(self.options['without-host'].value):
                link = url['url']
            else:
                link = "{0}://{1}{2}".format(
                    self.options['protocol'].value,
                    self.options['host'].value,
                    url['url']
                )
            print link

    def add_action(self):
        """ Action add of module """
        pid = Registry().get('pData')['id']
        self.validate_main()

        if self.model.exists(pid, self.options['host'].value, self.options['url'].value):
            raise WSException("URL '{0}' already exists in this project in host '{1}'!".
                              format(self.options['url'].value, self.options['host'].value))

        host_id = HostsModel().get_id_by_name(pid, self.options['host'].value)

        if (self.options['url'].value[-1] == '/' and
                self.model.exists(pid, self.options['host'].value, self.options['url'].value[:-1])) or\
            (self.options['url'].value[-1] != '/' and
             self.model.exists(pid, self.options['host'].value, self.options['url'].value + "/")):
            if raw_input('Url {0} have analogue in database (with or without end slash). '
                         'Are you realy want to add it (y/n)?'
                         .format(self.options['url'].value)).lower()[0] != 'y':
                print "Url {0} was not added!".format(self.options['url'].value)
                return

        self.model.add(
            Registry().get('pData')['id'],
            host_id,
            self.options['url'].value
        )

        print " URL '{0}' successfully added to host '{1}'".\
              format(self.options['url'].value, self.options['host'].value)

    def delete_action(self):
        """ Delete action of module """
        self.validate_main()

        if not self.model.exists(Registry().get('pData')['id'], self.options['host'].value, self.options['url'].value):
            raise WSException("URL '{0}' not exists in this project in host '{1}'!".
                              format(self.options['url'].value, self.options['host'].value))

        self.model.delete(Registry().get('pData')['id'], self.options['host'].value, self.options['url'].value)
        print "URL '{0}' in host '{1}' successfully deleted."\
              .format(self.options['host'].value, self.options['url'].value)

    def run(self, action):
        WSModule.run(self, action)
        self.done = True
