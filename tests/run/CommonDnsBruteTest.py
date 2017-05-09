# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Common class for DnsBrute* tests
"""

import os
import shutil

from CommonTest import CommonTest

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

class CommonDnsBruteTest(CommonTest):
    """ Common class for DnsBrute* tests """
    def setup(self):
        CommonTest.setup(self)
        shutil.copyfile(wrpath + '/bases/dns-servers.txt', '/tmp/dns-servers.old')

        fh = open(wrpath + '/bases/dns-servers.txt', 'w')
        fh.write("127.0.0.1")
        fh.close()

    def teardown(self):
        shutil.copyfile('/tmp/dns-servers.old', wrpath + '/bases/dns-servers.txt')

    def _prepare_db(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")
