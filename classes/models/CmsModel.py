# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class for work with cms* tables
"""

from classes.models.CommonModel import CommonModel
from libs.common import md5

class CmsModel(CommonModel):
    """ Class for work with cms* tables """
    def cms_list(self):
        """ List of CMS from DB """
        return self._db.fetch_pairs("SELECT id, name FROM cms")

    def all_paths_list(self):
        """ List of uniq CMS paths """
        return self._db.fetch_col("SELECT path FROM cms_paths_hashes")

    def get_hash_id_by_path(self, path):
        """ Return ID of hash by path from cms_paths_hashes table """
        return self._db.fetch_one(
            "SELECT id FROM `cms_paths_hashes` WHERE hash={0}"
            .format(self._db.quote(md5(path)))
        )

    def get_cms_by_hash_ids(self, hash_ids):
        """ Return a CMS list by hashes ids """
        return self._db.fetch_col(
            "SELECT DISTINCT cms_id FROM cms_paths WHERE hash_id IN({0})"
            .format(",".join(map(str, hash_ids)))
        )

    def get_cms_paths(self, cms_id):
        """ Get all paths of current CMS """
        return self._db.fetch_col(
            "SELECT h.path FROM `cms_paths` p, cms_paths_hashes h WHERE `cms_id`={0} AND p.hash_id = h.id"
            .format(cms_id)
        )
