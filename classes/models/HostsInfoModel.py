# -*- coding: utf-8 -*-
""" Class for work with hosts_info table """
from classes.models.CommonModel import CommonModel

class HostsInfoModel(CommonModel):
    """ Class for work with hosts_info table """
    def set_info(self, project_id, host_id, key, value):
        """ Set some info of host by id and info key """
        self._db.replace("hosts_info", {'project_id':project_id, 'host_id': host_id, 'key': key, 'value': value})
