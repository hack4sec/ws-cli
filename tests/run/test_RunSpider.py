# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of Spider module
"""
import sys
import os
import subprocess
import copy

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes')
sys.path.append(testpath + '/classes')
sys.path.append(wrpath + '/classes/models')
sys.path.append(wrpath + '/classes/jobs')
sys.path.append(wrpath + '/classes/threads')
sys.path.append(wrpath + '/classes/kernel')

from CommonTest import CommonTest
from classes.Registry import Registry
from libs.common import file_get_contents, md5

class Test_RunSpider(CommonTest):
    """Tests of Spider module"""
    model = None

    normal_test_data = {
        '/': {'response_code': 200, 'spidered': 1, 'referer': ''},
        '/not-exists.php': {'response_code': 404, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/not-exists.svg': {'response_code': 0, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/redirect-target.php': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/redirect.php'},
        '/redirect.php': {'response_code': 302, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/code.js': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/compressed.js': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/style.css': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/style-compressed.css': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/exists.php?a=1&b=2&c=3': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/exists.php?aa=1&bb=2&cc=3': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/slow.php': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/images.php?a=1': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/style.css'},
        '/images.php?a=2': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/style.css'},
        '/images.php?a=3': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/style.css'},
        '/images.php?a=4': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/style-compressed.css'},
        '/images.php?a=5': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/style-compressed.css'},
        '/images.php?a=6': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/style-compressed.css'},
        '/rss.php': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/atom.php': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/rss.php'},
        '/page.php?p=1': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/rss.php'},
        '/page.php?p=2': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/rss.php'},
        '/page.php?p=3': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/rss.php'},
        '/page.php?p=4': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/rss.php'},
        '/page.php?p=5&commentsrss=1': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/rss.php'},
        '/exists.php?customxml=0': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/custom-xml.php'},
        '/exists.php?customxml=1': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/custom-xml.php'},
        '/exists.php?customxml=2': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/custom-xml.php'},
        '/exists.php?customxml=3': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/custom-xml.php'},
        '/exists.php?customxml=4': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/custom-xml.php'},
        '/exists.php?customxml=5': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/custom-xml.php'},
        '/custom-xml.php': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/dir1': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/dir2': {'response_code': 403, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/exists.php?js=1': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/code.js'},
        '/exists.php?js=2': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/code.js'},
        '/exists.php?js=3': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/code.js'},
        '/exists.php?js=4': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/compressed.js'},
        '/exists.php?js=5': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/compressed.js'},
        '/exists.php?js=6': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/compressed.js'},
        '/exists.php?customxml=6': {'response_code': 200, 'spidered': 1,
                                    'referer': 'http://wrtest.com/syntax-error-xml.php'},
        '/exists.php?customxml=7': {'response_code': 200, 'spidered': 1,
                                    'referer': 'http://wrtest.com/syntax-error-xml.php'},
        '/exists.php?customxml=8': {'response_code': 200, 'spidered': 1,
                                    'referer': 'http://wrtest.com/syntax-error-xml.php'},
        '/exists.php?comment': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/syntax-error-xml.php': {'response_code': 200, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/exist': {'response_code': 404, 'spidered': 1, 'referer': 'http://wrtest.com/code.js'},
        '/exist2': {'response_code': 404, 'spidered': 1, 'referer': 'http://wrtest.com/compressed.js'},
        '/maxsize': {'response_code': 0, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/deep/': {'response_code': 403, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/deep/moredeep/': {'response_code': 403, 'spidered': 1, 'referer': 'http://wrtest.com/'},
        '/deep/moredeep/dir1/': {'response_code': 403, 'spidered': 1, 'referer': 'http://wrtest.com/'},
    }

    normal_test_files_content = {
        '/': 'Some text',
        '/not-exists.php': 'Not Found',
        '/exists.php?a=1&b=2&c=3': ' ok ',
        '/exists.php?aa=1&bb=2&cc=3': ' ok ',
        '/slow.php': '1111111',
        '/redirect-target.php': '123123123',
        '/style.css': 'font-color',
        '/code.js': 'var a',
        '/compressed.js': 'var a',
        '/atom.php': 'atom',
        '/rss.php': 'rss version="2.0"',
        '/page.php?p=1': 'page1',
        '/page.php?p=2': 'page2',
        '/page.php?p=3': 'page3',
        '/page.php?p=4': 'page4',
        '/page.php?p=5&commentsrss=1': 'page5',
        '/style-compressed.css': 'a{font-color:r',
        '/exists.php?customxml=0': ' ok ',
        '/exists.php?customxml=1': ' ok ',
        '/exists.php?customxml=2': ' ok ',
        '/exists.php?customxml=3': ' ok ',
        '/exists.php?customxml=4': ' ok ',
        '/exists.php?customxml=5': ' ok ',
        '/custom-xml.php': '<items>',
        '/dir1': 'some dir',
        '/dir2': 'Forbidden',
        '/exists.php?js=1': ' ok ',
        '/exists.php?js=2': ' ok ',
        '/exists.php?js=3': ' ok ',
        '/exists.php?js=4': ' ok ',
        '/exists.php?js=5': ' ok ',
        '/exists.php?js=6': ' ok ',
    }

    def _prepare_db(self, insert_root=True):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'prj', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', '')")
        if insert_root:
            self.db.q("INSERT INTO `urls`"
                      "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                      "size, when_add, who_add, descr, spidered)"
                      "VALUES(1, 1, 1, '6666cd76f96956469e7be39d750cc7d9', '/', '', 0, 0, 0, 1, 'human', '', 0)")

    def _scan(self, config, test_data, test_files_content, url_decrease, insert_root=True, additional_run_params=None):
        """
        Common scan method
        :param config:
        :param test_data:
        :param test_files_content:
        :param url_decrease:
        :param insert_root:
        :param additional_run_params:
        :return:
        """
        additional_run_params = additional_run_params or []

        self._prepare_db(insert_root)
        run_params = [
            './main.py', 'prj', 'Spider', 'scan', '--host=wrtest.com'
        ]
        run_params.extend(additional_run_params)
        run_params.append('--threads=3' if '--selenium=1' not in run_params else '--threads=1')

        self._replace_config(config)
        os.chdir(wrpath)
        out = subprocess.check_output(run_params)

        self._restore_config()
        self.output_errors(out)

        urls = self.db.fetch_all("SELECT * FROM urls ORDER BY id ASC")

        assert len(urls) == len(test_data)
        assert len(urls)-url_decrease == len(os.listdir(Registry().get('data_path') + 'wrtest.com/'))

        for url in urls:
            if url['url'] == '/slow.php':
                assert url['response_time'] > 4
            test_data_row = test_data[url['url']]
            for field in test_data_row:
                assert test_data_row[field] == url[field]

        for url in test_files_content:
            data = file_get_contents(Registry().get('data_path') + 'wrtest.com/' + md5(url))
            assert data.find(test_files_content[url]) > -1

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='/' AND parent_id=0 AND host_id=1") == 1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='deep' AND parent_id=1 AND host_id=1") == 1
        assert self.db.fetch_one(
            "SELECT COUNT(id) FROM urls_base WHERE name='moredeep' AND parent_id="
            "(SELECT id FROM urls_base WHERE name='deep' AND parent_id=1 AND host_id=1) AND host_id=1"
            ) == 1

        assert self.db.fetch_one(
            "SELECT COUNT(id) FROM urls_base WHERE name='dir1' AND parent_id="
            "(SELECT id FROM urls_base WHERE name='moredeep' AND host_id=1) AND host_id=1"
            ) == 1

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base_params") > 0

        return out

    def _get_test_data(self):
        """Get test data exemplar"""
        return copy.deepcopy(self.normal_test_data)

    def _get_test_files_content(self):
        """Get test file contents"""
        return copy.deepcopy(self.normal_test_files_content)

    def test_normal_selenium_scan(self):
        test_data = self._get_test_data()
        for url in test_data:
            if test_data[url]['response_code'] != 404:
                test_data[url]['response_code'] = 0

        del test_data['/page.php?p=3']
        del test_data['/page.php?p=2']
        del test_data['/page.php?p=4']
        del test_data['/redirect-target.php']
        del test_data['/exists.php?customxml=7']
        del test_data['/exists.php?customxml=8']
        del test_data['/page.php?p=5&commentsrss=1']
        del test_data['/images.php?a=6']
        del test_data['/images.php?a=5']
        del test_data['/images.php?a=4']
        del test_data['/images.php?a=3']
        del test_data['/images.php?a=2']
        del test_data['/images.php?a=1']
        del test_data['/atom.php']

        test_files_content = self._get_test_files_content()
        del test_files_content['/page.php?p=3']
        del test_files_content['/page.php?p=2']
        del test_files_content['/page.php?p=4']
        del test_files_content['/redirect-target.php']
        del test_files_content['/page.php?p=5&commentsrss=1']
        del test_files_content['/atom.php']

        for url in test_files_content:
            test_files_content[url] = test_files_content[url].strip()
        test_files_content['/rss.php'] = 'xml version="1.0"'

        self._scan(
            'normal',
            test_data,
            test_files_content,
            1,
            additional_run_params=[
                '--selenium=1',
                '--not-found-re',
                '<h1>Not Found</h1>',
                '--ddos-detect-phrase',
                'somephrasenotexists',
            ]
        )

    def test_requests_limit_scan(self):
        self._prepare_db()
        self._replace_config('requests-limit')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'prj', 'Spider', 'scan', '--host=wrtest.com', '--threads=2'
        ])
        self._restore_config()
        self.output_errors(out)

        spidered = self.db.fetch_one("SELECT COUNT(id) FROM urls WHERE spidered")
        not_spidered = self.db.fetch_one("SELECT COUNT(id) FROM urls WHERE !spidered")
        assert spidered < 30
        assert not_spidered

    def test_normal_scan(self):
        test_data = self._get_test_data()
        test_files_content = self._get_test_files_content()
        out = self._scan('normal', test_data, test_files_content, 2)
        assert out.count('but limit in config')
        assert out.count("Document syntax error") == 1

    def test_ignore_scan(self):
        test_data = self._get_test_data()
        del test_data['/page.php?p=5&commentsrss=1']
        test_files_content = self._get_test_files_content()
        del test_files_content['/page.php?p=5&commentsrss=1']
        out = self._scan('normal', test_data, test_files_content, 2, additional_run_params=['--ignore=commentsrss'])
        assert out.count('but limit in config')
        assert out.count("Document syntax error") == 1

    def test_only_one_scan(self):
        test_data = self._get_test_data()
        to_remove = [
            '/images.php?a=1', '/images.php?a=2', '/images.php?a=3', '/images.php?a=5', '/images.php?a=6'
        ]
        for rem in to_remove:
            del test_data[rem]

        test_files_content = self._get_test_files_content()

        out = self._scan('normal', test_data, test_files_content, 2, additional_run_params=['--only-one=images'])
        assert bool(out.count('but limit in config'))
        assert out.count("Document syntax error") == 1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls WHERE url LIKE '/images.php%'") == 1

    def test_normal_scan_without_root_url(self):
        self.db.q("TRUNCATE urls")
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 0
        test_data = self._get_test_data()
        test_files_content = self._get_test_files_content()
        out = self._scan('normal', test_data, test_files_content, 2, insert_root=False)
        assert bool(out.count('but limit in config'))
        assert out.count("Document syntax error") == 1
        assert bool(out.count("Root URL was added"))

    def test_enable_mime_scan(self):
        test_data = self._get_test_data()
        to_remove = [
            '/images.php?a=1', '/images.php?a=2', '/images.php?a=3',
            '/images.php?a=4', '/images.php?a=5', '/images.php?a=6',
            '/atom.php', '/exists.php?customxml=0', '/exists.php?customxml=1',
            '/exists.php?customxml=2', '/exists.php?customxml=3',
            '/exists.php?customxml=4', '/exists.php?customxml=5', '/exists.php?js=1',
            '/exists.php?js=2', '/exists.php?js=3',
            '/exists.php?js=4', '/exists.php?js=5', '/exists.php?js=6', '/page.php?p=1',
            '/page.php?p=2', '/page.php?p=3',
            '/page.php?p=4', '/page.php?p=5&commentsrss=1',
            '/exists.php?customxml=6', '/exists.php?customxml=7',
            '/exists.php?customxml=8', '/exist', '/exist2'
        ]
        for rem in to_remove:
            del test_data[rem]


        test_data['/rss.php']['response_code'] = 0
        test_data['/custom-xml.php']['response_code'] = 0
        test_data['/syntax-error-xml.php']['response_code'] = 0
        test_data['/style-compressed.css']['response_code'] = 0
        test_data['/style.css']['response_code'] = 0
        test_data['/compressed.js']['response_code'] = 0
        test_data['/code.js']['response_code'] = 0

        test_files_content = self._get_test_files_content()
        to_remove = [
            '/atom.php', '/exists.php?customxml=0', '/exists.php?customxml=1',
            '/exists.php?customxml=2', '/exists.php?customxml=3',
            '/exists.php?customxml=4', '/exists.php?customxml=5', '/exists.php?js=1',
            '/exists.php?js=2', '/exists.php?js=3',
            '/exists.php?js=4', '/exists.php?js=5', '/exists.php?js=6',
            '/page.php?p=1', '/page.php?p=2', '/page.php?p=3',
            '/page.php?p=4', '/page.php?p=5&commentsrss=1', '/style.css',
            '/compressed.js', '/code.js', '/style-compressed.css',
            '/custom-xml.php', '/rss.php'

        ]
        for rem in to_remove:
            del test_files_content[rem]

        self._scan('enable-mime', test_data, test_files_content, 9)

    def test_disable_mime_scan(self):
        test_data = self._get_test_data()

        test_data['/code.js']['response_code'] = 0
        test_data['/compressed.js']['response_code'] = 0
        del test_data['/exists.php?js=1']
        del test_data['/exists.php?js=2']
        del test_data['/exists.php?js=3']
        del test_data['/exists.php?js=4']
        del test_data['/exists.php?js=5']
        del test_data['/exists.php?js=6']
        del test_data['/exist']
        del test_data['/exist2']

        test_files_content = self._get_test_files_content()
        del test_files_content['/code.js']
        del test_files_content['/compressed.js']
        del test_files_content['/exists.php?js=1']
        del test_files_content['/exists.php?js=2']
        del test_files_content['/exists.php?js=3']
        del test_files_content['/exists.php?js=4']
        del test_files_content['/exists.php?js=5']
        del test_files_content['/exists.php?js=6']

        out = self._scan('disable-mime', test_data, test_files_content, 4)
        assert bool(out.count('but limit in config'))
        assert out.count("Document syntax error") == 1

    def test_full_new_scan(self):
        self._prepare_db()

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'prj', 'Spider', 'scan', '--host=wrtest.com', '--threads=3'
        ])
        self.output_errors(out)
        assert not out.count("Total links count: 0")

        out = subprocess.check_output([
            './main.py', 'prj', 'Spider', 'scan', '--host=wrtest.com', '--threads=3'
        ])
        self.output_errors(out)
        assert bool(out.count("Total links count: 0"))

        out = subprocess.check_output([
            './main.py', 'prj', 'Spider', 'scan', '--host=wrtest.com', '--threads=3', '--full-new=1'
        ])
        self.output_errors(out)
        assert not out.count("Total links count: 0")

        self._restore_config()

    def test_error_host_not_exists(self):
        self._prepare_db()
        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'prj', 'Spider', 'scan', '--host=notfound.com', '--threads=3'
        ])
        self._restore_config()
        self.output_errors(out)
        assert bool(out.count('not found in this project'))
