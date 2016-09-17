# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class for work with urls table
"""

import time

from libs.common import md5
from classes.Registry import Registry
from classes.kernel.WSException import WSException
from classes.models.HostsModel import HostsModel


class UrlsModel(object):
    """ Class for work with urls table """
    _db = None

    def __init__(self):
        self._db = Registry().get('ndb')

    def add(
            self, pid, host_id, url, referer='', response_code=0,
            response_time=0, who_add='human', spidered=0, size=0, descr=''
    ):
        """ Add url to table """
        try:
            return self._db.insert(
                "urls",
                {
                    "project_id": pid,
                    "host_id": host_id,
                    "hash": md5(url),
                    "url": url,
                    "referer": referer,
                    "response_code": response_code,
                    "response_time": response_time,
                    "when_add": int(time.time()),
                    "who_add": who_add,
                    "spidered": spidered,
                    "size": size,
                    "descr": descr
                },
                1
            )
        except BaseException as e:
            if Registry().isset('logger'):
                Registry().get('logger').ex(e)
            else:
                print "Can`t add url: " + str(e)

    def add_mass(self, pid, host_id, data):
        """ Add many urls at once in table """
        to_insert = []
        for row in data:
            for field in ['url', 'referer', 'response_code', 'response_time', 'who_add', 'spidered', 'size', 'descr']:
                if field not in row.keys():
                    if field in ['referer', 'response_code', 'response_time', 'descr']:
                        row[field] = ''
                    elif field in ['spidered', 'size']:
                        row[field] = 0
                    elif field == 'who_add':
                        row[field] = 'human'
                    elif field == 'url':
                        raise WSException("URL row must have a 'url' key")

            for k in row.keys():
                if k not in [
                        'url', 'referer', 'response_code', 'response_time', 'who_add', 'spidered', 'size', 'descr'
                ]:
                    raise WSException("Key '{0}' must not be in url data".format(k))

            to_insert.append({
                'project_id': pid,
                "host_id": host_id,
                "hash": md5(row['url']),
                "url": row['url'],
                "referer": row['referer'],
                "response_code": row['response_code'],
                "response_time": row['response_time'],
                "when_add": int(time.time()),
                "who_add": row['who_add'],
                "spidered": row['spidered'],
                "size": row['size'],
                "descr": row['descr']

            })

            if len(to_insert)%50 == 0:
                self._db.insert_mass("urls", to_insert, 1)
                to_insert = []

        if len(to_insert):
            self._db.insert_mass("urls", to_insert, 1)

        return True

    def list_by_host_name(self, project_id, host, like=""):
        """ Get urls list by host name and project_id """
        host_id = HostsModel().get_id_by_name(project_id, host)

        like_expr = "" \
                    if not len(like.strip()) \
                    else " AND url LIKE '%{0}%' ".format(self._db.escape(like.strip()))

        return self._db.fetch_all(
            "SELECT url, response_code as code, response_time as time, when_add, who_add, descr, size FROM urls "
            "WHERE project_id = {0} AND host_id = {1} ".format(project_id, host_id) + like_expr +
            "ORDER BY url"
        )

    def list_by_host_name_for_spider(self, project_id, host):
        """ Get urls list by host name and project_id, but in special format for spider """
        host_id = HostsModel().get_id_by_name(project_id, host)

        return self._db.fetch_all(
            "SELECT url, response_code as code, response_time as time, when_add, who_add, descr FROM urls "
            "WHERE project_id = {0} AND host_id = {1} AND !spidered "
            "ORDER BY url".format(project_id, host_id)
        )

    def exists(self, project_id, host, url):
        """ Is url exists? """
        host_id = HostsModel().get_id_by_name(project_id, host)

        return self._db.fetch_one(
            "SELECT 1 FROM urls WHERE project_id = {0} AND host_id={1} AND hash = '{2}'"
            .format(project_id, host_id, md5(url))
        )

    def delete(self, project_id, host, url):
        """ Delete url from table """
        host_id = HostsModel().get_id_by_name(project_id, host)
        self._db.q(
            "DELETE FROM urls WHERE project_id = {0} AND host_id = {1} AND hash = {2} "
            .format(project_id, host_id, self._db.quote(md5(url)))
        )

    def update_url_field(self, project_id, host, url, field, value):
        """ Update custom field of current url """
        host_id = HostsModel().get_id_by_name(project_id, host)
        return self._db.update(
            "urls",
            {field: value},
            "hash = '{0}' AND project_id = {1} AND host_id = {2}".format(md5(url), project_id, host_id)
        )

    def update_url_field_mass(self, project_id, host, field, data):
        """ Mass update custom field of many urls """
        host_id = HostsModel().get_id_by_name(project_id, host)

        update = {}
        for row in data:
            case = "host_id = '{0}' AND `hash` = '{1}' ".format(host_id, md5(row['url']))
            update[case] = row['value']

        self._db.update_mass("urls", field, update)






