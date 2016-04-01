# -*- coding: utf-8 -*-
""" Class for work with urls_base* tables """

import time

from libs.common import md5
from classes.models.CommonModel import CommonModel
from classes.Registry import Registry

class UrlsBaseModel(CommonModel):
    """ Class for work with urls_base* tables """
    _pathCache = {}

    def _get_insert_row(self, path, host_id, parent_id):
        """ Build and return ready row to insert in DB """
        return {
            'host_id': host_id,
            'project_id': Registry().get('pData')['id'],
            'name': path,
            'parent_id': parent_id,
            'when_add': int(time.time()),
        }

    def _path_exists(self, host_id, parent_id, name):
        """ Is current path exists? """
        _hash = md5("{0}-{1}-{2}".format(host_id, parent_id, name))
        if _hash not in self._pathCache.keys():
            self._pathCache[_hash] = \
                self._db.fetch_one(
                    'SELECT id FROM urls_base WHERE host_id = {0} AND parent_id = {1} AND name = {2}'.
                    format(int(host_id), int(parent_id), self._db.quote(name))
                )
        return self._pathCache[_hash]

    def _add_path_cache(self, host_id, parent_id, name, _id):
        """ Add branch id to path-cache """
        _hash = md5("{0}-{1}-{2}".format(host_id, parent_id, name))
        self._pathCache[_hash] = _id

    def add_url(self, host_id, url):
        """ Add url in database (with break on parts) """
        params = url.split('?')[1] if url.count('?') else ''
        url = url.split('?')[0]

        parent_id = 0

        if url == '/':
            if not self._path_exists(host_id, 0, '/'):
                new_parent_id = self._db.insert("urls_base", self._get_insert_row(url, host_id, 0))
                self._add_path_cache(host_id, 0, '/', new_parent_id)
        else:
            url = url.split('/')
            for url_part in url:
                if url_part == '':
                    if parent_id != 0:
                        continue

                    new_parent_id = self._path_exists(host_id, 0, '/')
                    if new_parent_id is None:
                        new_row = self._get_insert_row('/', host_id, 0)
                        try:
                            new_parent_id = self._db.insert("urls_base", new_row)
                            self._add_path_cache(host_id, 0, '/', new_parent_id)
                        except BaseException:
                            pass

                    parent_id = new_parent_id
                else:
                    new_parent_id = self._path_exists(host_id, parent_id, url_part)
                    if new_parent_id is None:
                        new_row = self._get_insert_row(url_part, host_id, parent_id)
                        new_parent_id = self._db.insert("urls_base", new_row)
                        self._add_path_cache(host_id, parent_id, url_part, new_parent_id)

                    parent_id = new_parent_id

        if len(params):
            for param in params.split('&'):
                self._db.insert('urls_base_params', {'parent_id': parent_id, 'name': param.split("=")[0]}, True)

