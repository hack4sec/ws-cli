# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class for work with hosts_info table
"""
from classes.models.CommonModel import CommonModel

class HostsInfoModel(CommonModel):
    """ Class for work with hosts_info table """
    def set_info(self, project_id, host_id, key, value):
        """ Set some info of host by id and info key """
        self._db.replace("hosts_info", {'project_id':project_id, 'host_id': host_id, 'key': key, 'value': value})
