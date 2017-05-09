# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of FormBruter module
"""
import sys
import os
import time
import pytest
import requests

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
from libs.common import file_get_contents, t


class Test_RunFormBruter(CommonTest):
    """Tests of FormBruter module"""
    check_method = None
    selenium = False
    use_https = False


    def setup(self):
        CommonTest.setup(self)

        requests.get("http://wrtest.com/?clean_log=1")
        requests.get("http://wrtest.com/?protect_disable=1")
        requests.get("http://wrtest.com/?found_disable=1")

    def _prepare_db(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")

    def _logger(self, first_stop=False):
        """
        Check logger work
        :param first_stop:
        :param selenium:
        :return:
        """
        logs_path = "{0}/logs/form-bruter/{1}/".format(wrpath, t("%Y-%m-%d"))
        time_dir = sorted(os.listdir(logs_path))[-1]

        run_log_data = file_get_contents("{0}/{1}/run.log".format(logs_path, time_dir))
        assert "Loaded 4 words from source" in run_log_data
        assert "qwerty" in run_log_data

        assert os.path.exists("{0}/{1}/items/123.txt".format(logs_path, time_dir))
        assert os.path.exists("{0}/{1}/items/test.txt".format(logs_path, time_dir))
        assert os.path.exists("{0}/{1}/items/qwerty.txt".format(logs_path, time_dir))
        assert os.path.exists("{0}/{1}/items/abcde.txt".format(logs_path, time_dir)) == (not first_stop)

        assert '<input type="password" name="password" />' \
               in file_get_contents("{0}/{1}/items/123.txt".format(logs_path, time_dir))
        assert '<input type="password" name="password" />' \
               in file_get_contents("{0}/{1}/items/test.txt".format(logs_path, time_dir))
        assert '<input type="password" name="password" />' \
               not in file_get_contents("{0}/{1}/items/qwerty.txt".format(logs_path, time_dir))
        assert 'Success!' in file_get_contents("{0}/{1}/items/qwerty.txt".format(logs_path, time_dir))

    brute_data = [
        (True, False, False),
        (False, True, False),
        (True, False, True),
        (False, True, True),
    ]
    @pytest.mark.parametrize("true_phrase,false_phrase,selenium", brute_data)
    def test_brute(self, true_phrase, false_phrase, selenium):
        self._prepare_db()
        run_params = [
            './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
            '--login', 'root', '--dict', 'tests/run/files/pass.txt',
        ]
        if true_phrase:
            run_params.append('--true-phrase=Success')
        if false_phrase:
            run_params.append('--false-phrase')
            run_params.append('type="password"')
        if selenium:
            run_params.append('--selenium=1')
            run_params.append('--ddos-detect-phrase=aaaa')
            run_params.append('--conffile')
            run_params.append('tests/run/files/form-bruter-true.cfg')
        else:
            run_params.append('--confstr')
            run_params.append('login=^USER^&password=^PASS^')

        out = self._run('normal', run_params)
        self.output_errors(out)
        assert 'qwerty' in out
        assert out.count("Passwords found:") == 1
        self._logger()

    def test_brute_delay(self):
        self._prepare_db()
        stime = int(time.time())
        self._run('normal', [
            './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
            '--confstr', 'login=^USER^&password=^PASS^', '--login', 'root', '--dict', 'tests/run/files/pass.txt',
            '--true-phrase', 'Success!'
        ])
        first_time = int(time.time()) - stime
        time.sleep(1)
        stime = int(time.time())
        self._run('normal', [
            './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
            '--confstr', 'login=^USER^&password=^PASS^', '--login', 'root', '--dict', 'tests/run/files/pass.txt',
            '--true-phrase', 'Success!', '--delay=2'
        ])
        second_time = int(time.time()) - stime
        assert second_time/first_time >= 3

    positives_data = [
        (True),
        (False),
    ]
    @pytest.mark.parametrize("selenium", positives_data)
    def test_brute_many_positives(self, selenium):
        requests.get("http://wrtest.com/?found_enable=1")
        self._prepare_db()
        run_params = [
            './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
            '--login', 'root', '--dict', 'tests/run/files/dafs-mp.txt', '--false-phrase', 'type="password"'
        ]

        if selenium:
            run_params.append('--selenium=1')
            run_params.append('--ddos-detect-phrase=aaaa')
            run_params.append('--conffile')
            run_params.append('tests/run/files/form-bruter-true.cfg')
        else:
            run_params.append('--confstr')
            run_params.append('login=^USER^&password=^PASS^')

        out = self._run('many-positives', run_params)
        self.output_errors(out)
        assert 'Many positive detections' in out

    first_stop_data = [
        (True),
        (False),
    ]
    @pytest.mark.parametrize('selenium', first_stop_data)
    def test_first_stop(self, selenium):
        self._prepare_db()
        run_params = [
            './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
            '--login', 'root', '--dict', 'tests/run/files/pass.txt',
            '--true-phrase', 'Success!', '--first-stop=1'
        ]
        if selenium:
            run_params.append('--selenium=1')
            run_params.append('--conffile')
            run_params.append('tests/run/files/form-bruter-false.cfg')
        else:
            run_params.append('--confstr')
            run_params.append('login=^USER^&password=^PASS^')

        out = self._run('normal', run_params)
        self.output_errors(out)
        assert 'qwerty' in out
        assert out.count("Passwords found:") == 1

        self._logger(first_stop=True)

    selenium_scan_protect_data = [
        (True, '--ddos-detect-phrase=PROTECTION', False),
        (True, '--ddos-detect-phrase=PROTECTION', True),
        (False, '', False),
        (True, '--ddos-human-action=PROTECTION', False),
    ]
    @pytest.mark.parametrize("use_protect,protect_param,use_https", selenium_scan_protect_data)
    def test_selenium_scan_protection(self, use_protect, protect_param, use_https):
        self._prepare_db()
        self.check_method = 'get'
        self.selenium = True
        self.use_https = use_https

        run_params = [
            './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
            '--conffile', 'tests/run/files/form-bruter-true.cfg', '--login', 'root', '--dict',
            'tests/run/files/pass.txt', '--true-phrase', 'Success!', '--selenium=1'
        ]
        if use_protect:
            requests.get("http://wrtest.com/?protect_enable=1")
            run_params.append(protect_param)
        if use_https:
            run_params.append('--protocol=https')

        out = self._run('normal', run_params)
        self.output_errors(out)
        assert 'qwerty' in out
        assert out.count("Passwords found:") == 1

        self._logger()

    error_cmds = [
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--conffile', 'tests/run/files/form-bruter-false.cfg', '--login', 'root', '--dict', 'not/exists.txt',
                '--true-phrase', 'Success!', '--selenium=1', '--ddos-detect-phrase=aaaa', '--first-stop=1'
            ],
            'not exists or not readable'
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'notfound.com', '--url', '/auth.php',
                '--threads=1',
                '--conffile', 'tests/run/files/form-bruter-false.cfg', '--login', 'root', '--dict',
                'tests/run/files/pass.txt',
                '--true-phrase', 'Success!', '--selenium=1', '--ddos-detect-phrase=aaaa', '--first-stop=1'
            ],
            'not found in this project'
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--conffile', 'tests/run/files/form-bruter-false.cfg', '--login', 'root', '--dict',
                'tests/run/files/pass.txt',
                '--true-phrase', 'Success!', '--selenium=1', '--ddos-detect-phrase=aaaa', '--first-stop=1',
                '--protocol=aaa'
            ],
            'Protocol param must be '
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--conffile', 'tests/run/files/form-bruter-false.cfg', '--login', 'root', '--dict',
                'tests/run/files/pass.txt',
                '--true-phrase', 'Success!', '--selenium=1', '--ddos-detect-phrase=aaaa', '--first-stop=1', '--parts=a',
                '--part=1'
            ],
            'Parts param must be digital, but'
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--conffile', 'tests/run/files/form-bruter-false.cfg', '--login', 'root', '--dict',
                'tests/run/files/pass.txt',
                '--true-phrase', 'Success!', '--selenium=1', '--ddos-detect-phrase=aaaa', '--first-stop=1', '--part=a',
                '--parts=2'
            ],
            'Part param must be digital, but'
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--conffile', 'tests/run/files/form-bruter-false.cfg', '--login', 'root', '--dict',
                'tests/run/files/pass.txt',
                '--true-phrase', 'Success!', '--selenium=1', '--ddos-detect-phrase=aaaa', '--first-stop=1', '--part=1'
            ],
            "If you use '--part' param, you must specify '--parts'"
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--conffile', 'tests/run/files/form-bruter-false.cfg', '--login', 'root', '--dict',
                'tests/run/files/pass.txt',
                '--true-phrase', 'Success!', '--selenium=1', '--ddos-detect-phrase=aaaa', '--first-stop=1', '--parts=1'
            ],
            "If you use '--parts' param, you must specify '--part'"
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--conffile', 'tests/run/files/form-bruter-false.cfg', '--login', 'root', '--dict',
                'tests/run/files/pass.txt',
                '--true-phrase', 'Success!', '--selenium=1', '--ddos-detect-phrase=aaaa', '--first-stop=1', '--parts=1',
                '--part=2'
            ],
            "Number of part"
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--conffile', 'tests/run/files/form-bruter-false.cfg', '--login', 'root', '--dict',
                'tests/run/files/pass.txt',
                '--true-phrase', 'Success!', '--selenium=1', '--ddos-detect-phrase=aaaa', '--first-stop=1', '--delay=a'
            ],
            'Delay param must be digital, but'
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--conffile', 'not/found.txt', '--login', 'root', '--dict', 'tests/run/files/pass.txt',
                '--true-phrase', 'Success!', '--selenium=1', '--ddos-detect-phrase=aaaa', '--first-stop=1'
            ],
            'Config file'
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--login', 'root', '--dict', 'tests/run/files/pass.txt',
                '--true-phrase', 'Success!', '--selenium=1', '--ddos-detect-phrase=aaaa', '--first-stop=1'
            ],
            'You must specify param --conffile'
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--login', 'root', '--dict', 'tests/run/files/pass.txt',
                '--true-phrase', 'Success!', '--first-stop=1'
            ],
            'You must specify param --confstr'
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--login', 'root', '--dict', 'tests/run/files/pass.txt', '--first-stop=1', '--confstr',
                'login=^USER^&password=^PASS^'
            ],
            'You must specify --false-phrase param or --true-phrase param'
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--login', 'root', '--dict', 'tests/run/files/pass.txt', '--first-stop=1', '--confstr',
                'login=a&password=^PASS^',
                '--true-phrase', 'Success!',
            ],
            "--confstr must have a ^USER^ fragment"
        ),
        (
            [
                './main.py', 'test', 'FormBruter', 'brute', '--host', 'wrtest.com', '--url', '/auth.php', '--threads=1',
                '--login', 'root', '--dict', 'tests/run/files/pass.txt', '--first-stop=1', '--confstr',
                'login=^USER^&password=a',
                '--true-phrase', 'Success!',
            ],
            "--confstr must have a ^PASS^ fragment"
        ),
    ]
    @pytest.mark.parametrize("cmd_set,check_phrase", error_cmds)
    def test_error(self, cmd_set, check_phrase):
        self._prepare_db()
        out = self._run('normal', cmd_set)
        assert out.count(check_phrase)
