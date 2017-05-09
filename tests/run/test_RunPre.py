# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of Pre module
"""
import sys
import os
import subprocess
import shutil

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath)
sys.path.append(wrpath + '/classes')
sys.path.append(testpath + '/classes')
sys.path.append(wrpath + '/classes/models')
sys.path.append(wrpath + '/classes/jobs')
sys.path.append(wrpath + '/classes/threads')
sys.path.append(wrpath + '/classes/kernel')

from CommonTest import CommonTest

class Test_RunPre(CommonTest):
    """Tests of Pre module"""
    def setup(self):
        CommonTest.setup(self)

        shutil.copyfile(wrpath + '/bases/pre-dafs-dirs.txt', '/tmp/pre-dafs-dirs.old')
        shutil.copyfile(wrpath + '/bases/pre-dafs-files.txt', '/tmp/pre-dafs-files.old')

        shutil.copyfile(wrpath + '/tests/run/files/pre-dafs-files.txt', wrpath + '/bases/pre-dafs-files.txt')
        shutil.copyfile(wrpath + '/tests/run/files/pre-dafs-dirs.txt', wrpath + '/bases/pre-dafs-dirs.txt')

    def teardown(self):
        shutil.copyfile('/tmp/pre-dafs-dirs.old', wrpath + '/bases/pre-dafs-dirs.txt')
        shutil.copyfile('/tmp/pre-dafs-files.old', wrpath + '/bases/pre-dafs-files.txt')

    def test_scan(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts_info") == 0
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 0

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Pre', 'scan', '--host=wrtest.com', '--dns=127.0.0.1'
        ])
        self._restore_config()
        self.output_errors(out)
        result = self.db.fetch_pairs("SELECT `key`, `value` FROM hosts_info")

        assert bool(result['backups'].count('www.zip') and result['backups'].count('www_old'))

        assert result['robots_txt'] == '1'
        assert result['encodings'] == '{"html": "utf-8", "http": "utf-8"}'
        assert result['nf'] == '{"files": 404, "dirs": 404}'
        assert result['powered_by'] == '["Powered by <b>WR3</b></"]'
        assert result['sitemap'].count('sitemap.xml') == 1
        assert result['sitemap'].count('sitemap2.xml') == 1
        assert result['ns'].count('127.0.0.1') == 2
        assert result['ns'].count('aaa.wrtest.com') == 1
        assert result['ns'].count('www.wrtest.com') == 1
        assert result['ns_always_true'] == '"0"'
        assert result['headers'].lower().find('x-powered-by') > -1
        assert result['dafs_dirs'] == '[{"url": "/files/", "code": 403, "time": 0}]'
        assert result['dafs_files'] == \
               '[{"url": "/index.php", "code": 200, "time": 0}, {"url": "/robots.txt", "code": 200, "time": 0}]'

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts_info") == 11

        test_urls = [
            '/sitemap.php?a=4', '/sitemap.php?a=3', '/sitemap.php?a=2', '/sitemap.php?a=1',
            '/robots.txt', '/index.php', '/files/', '/dir2_old/', '/sitemap.xml', '/sitemap2.xml'
        ]
        urls = self.db.fetch_col("SELECT url FROM urls")
        for url in urls:
            if url in test_urls:
                del test_urls[test_urls.index(url)]
        assert len(test_urls) == 0
