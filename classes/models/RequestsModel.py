# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class for work with requests table
"""

import json

from libs.common import md5
from classes.models.CommonModel import CommonModel

class RequestsModel(CommonModel):
    """ Class for work with requests table """
    def add(self, project_id, host_id, path, params, headers, method, protocol, founder, comment):
        """ Add request row to DB """
        _hash = self._build_hash(project_id, host_id, path, params, method, protocol)
        return self._db.insert(
            "requests",
            {
                "hash": _hash,
                "project_id": project_id,
                "host_id": host_id,
                "path": path,
                "params": params,
                "headers": json.dumps(headers),
                "method": method,
                "protocol": protocol,
                "founder": founder,
                "comment": comment
            },
            1
        )

    def _build_hash(self, project_id, host_id, path, params, method, protocol):
        """ Build hash of request """
        return md5("{0}|{1}|{2}|{3}|{4}|{5}".format(project_id, host_id, path, params, method, protocol))
