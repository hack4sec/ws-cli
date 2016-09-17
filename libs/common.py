# -*- coding: utf-8 -*-

"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Library with common used functions
"""

import os
import re
import hashlib
import locale
import time

import requests
import configparser

from classes.Registry import Registry

def file_to_list(path, unique=True):
    """ Split text file on lines, remove dups (if need), and return list of it """
    result = map(str.strip, open(path).readlines())
    return result if not unique else list(set(result))


def nformat(num):
    """ Return number formatted by locale from config """
    locale.setlocale(locale.LC_ALL, Registry().get('config')['main']['locale'].encode())
    return locale.format("%d", int(num), grouping=True)


def secs_to_text(secs):
    """ Convert number of seconds to human string - *d*h*m*s """
    secs = int(secs)

    min_time = 60
    hour_time = 3600
    day_time = 3600*24

    days = 0
    hours = 0
    mins = 0

    if secs >= day_time:
        days = secs / day_time
        secs = secs % day_time

    if secs >= hour_time:
        hours = secs / hour_time
        secs = secs % hour_time

    if secs >= min_time:
        mins = secs / min_time
        secs = secs % min_time

    str_time = []
    if days:
        str_time.append("{0}d".format(days))
    if hours:
        str_time.append("{0}h".format(hours))
    if mins:
        str_time.append("{0}m".format(mins))
    str_time.append("{0}s".format(secs))

    return " ".join(str_time)


def main_help():
    """ Main help function (usage) """
    config = configparser.ConfigParser()
    config.read(os.getcwd() + '/' + 'config.ini')
    print "Web-Scout " + config['main']['version']
    print "Usage: ./main.py projectName moduleName actionName [-h|args]"
    exit(0)


def validate_ip(ip):
    """ Regex IPv4 validator """
    return bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip))


def validate_host(host):
    """ Regex hostname validator """
    return bool(re.match(r'^[\da-z\.-]+\.[a-z]{2,6}$', host))


def validate_uri_start(url):
    """ Regex validator start of url """
    return bool(re.match(r'^(http:|https:|)//([\da-z\.-]+\.[a-z]{2,6})', url))


def md5(string):
    """ String to MD5-hash """
    m = hashlib.md5()
    #m.update(string.decode(encoding='UTF-8',errors='ignore').encode('UTF-8', errors='ignore'))
    m.update(string.encode('UTF-8'))
    return m.hexdigest()


def parse_split_conf(conf):
    """ Function parse comma separated values from config """
    result = []

    if len(conf.strip()):
        conf = conf.split(',')
        for item in conf:
            index = conf.index(item)
            conf[index] = item.encode('utf8')
        result = list(map(str.strip, conf))

    return result


def file_put_contents(path_to_file, content, add=False):
    """ Function put content to a file (analog of php file_put_contents()) """
    fh = open(path_to_file, 'a' if add else 'w')
    fh.write(content)
    fh.close()


def file_get_contents(path_to_file):
    """ Function get content of file (analog of php file_get_contents()) """
    fh = open(path_to_file, 'r')
    content = fh.read()
    fh.close()
    return content


def t(_format):
    """ Wrapper for time.strftime(*, time.localtime()) """
    return time.strftime(_format, time.localtime())


def mongo_result_to_list(mongo_result):
    """ Convert object of mongodb result to list """
    result = []
    for row in mongo_result:
        result.append(row)
    return result


def clear_double_slashes(_str):
    """ Recursive clear double slashes from str """
    while _str.count("//"):
        _str = _str.replace("//", "/")
    return _str


def always_not_404(protocol, host):
    """ Are host return on not-found request not 404 answer? """
    is_it = True
    for item in ['dv3fegseg', 'glg0j4', 'gw4ogk0']:
        resp = requests.get("{0}://{1}/{2}".format(protocol, host, item))
        if resp.status_code == 404:
            is_it = False
            break
    return is_it


def is_binary_content_type(content_type):
    """ Is this content-type is binary? """
    text_patterns = ['xml', 'javascript', 'html', 'text', 'plain', 'css', 'json']
    for pattern in text_patterns:
        if content_type.count(pattern):
            return False
    return True

def md5sum(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()