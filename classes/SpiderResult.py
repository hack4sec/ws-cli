# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class for report build from Spider module
"""

import re

from classes.Registry import Registry
from libs.common import mongo_result_to_list

class SpiderResult(object):
    """ Class for report build from Spider module """
    def __str__(self):
        stat = self.common_stat()
        result = ''

        result += 'Slowest links:\n'
        for link in stat['slow_links']:
            result += '\tURL:' + link['url'] + ' time:' + str(link['time']) + ' code:' + str(link['code']) + '\n'

        result += "\nTotal links count: {0}\n".format(Registry().get('mongo').spider_urls.count())

        return result

    def common_stat(self):
        """ Return common stat by response codes, slow links and files extensions """
        return {
            #'codes': self._get_codes_stat(),
            'slow_links': self._get_slowest_links(),
            #'extensions': self._get_extensions()
        }

    def _get_extensions(self):
        """ Build files extensions list """
        result = {}
        coll = Registry().get('mongo').spider_urls
        links = coll.group({'path': True}, '', {}, 'function () {}')
        links = mongo_result_to_list(links)

        exts = []
        for link in links:
            if link['path'].rfind('.') > -1 and len(link['path']) - link['path'].rfind('.') <= 5:
                exts.append(link['path'][link['path'].rfind('.'):])

        for ext in list(set(exts)):
            if ext not in result:
                result[ext] = []

            links = coll.find({'path': re.compile('\\' + ext + '$')})
            links = mongo_result_to_list(links)

            for link in links:
                result[ext].append(link['path'] + '?' + link['query'] if link['query'] else link['path'])

        return result

    def _get_slowest_links(self):
        """ Build slow links list """
        result = []
        data = Registry().get('mongo').spider_urls\
            .find({}, {'path': 1, 'query': 1, 'time': 1, 'code': 1})\
            .sort('time', -1)\
            .limit(int(Registry().get('config')['spider']['stat_slowest_links_count']))

        for link in mongo_result_to_list(data):
            link['url'] = link['path'] + '?' + link['query'] if link['query'] else link['path']
            del link['path'], link['query'], link['_id']
            result.append(link)

        return result

    def _get_codes_stat(self):
        """ Build dict with http-codes and their counts """
        coll = Registry().get('mongo').spider_urls
        result = {}

        codes = coll.group({'code': True}, '', {}, 'function () {}')
        for code in codes:
            links = []
            code = code['code']
            data = coll.find({'code': code}, {'path': 1, 'query': 1})
            for link in mongo_result_to_list(data):
                links.append(link['path'] + '?' + link['query'] if link['query'] else link['path'])
            result[int(code)] = links

        return result
