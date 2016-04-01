# -*- coding: utf-8 -*-
""" Class for work with ips table """

from classes.models.CommonModel import CommonModel

class IpsModel(CommonModel):
    """ Class for work with ips table """

    def get_id_or_add(self, project_id, ip):
        """ Method add IPv4 in db and return it ID, or (if IPv4 exists in db) just return ID """
        ip_id = self._db.fetch_one(
            "SELECT id FROM ips WHERE project_id = {0} AND ip= {1} "
            .format(self._db.quote(project_id), self._db.quote(ip))
        )
        return self.add(project_id, ip, "") if not ip_id else ip_id

    def get_id(self, project_id, ip):
        """ Get id of IPv4 """
        return self._db.fetch_one(
            "SELECT id FROM ips WHERE project_id = {0} AND ip= {1} "
            .format(self._db.quote(project_id), self._db.quote(ip))
        )

    def exists(self, project_id, ip):
        """ Is IP exists in this project? """
        return self._db.fetch_one(
            "SELECT 1 FROM ips WHERE project_id = {0} AND ip= {1} "
            .format(self._db.quote(project_id), self._db.quote(ip))
        )

    def add(self, project_id, ip, descr):
        """ Add ip to table """
        return self._db.insert("ips", {"project_id": project_id, "ip": ip, "descr": descr})

    def list(self, project_id):
        """ Get IPs list of project """
        return self._db.fetch_all(
            "SELECT id, ip, descr FROM ips WHERE project_id = {0} ORDER BY id ASC"
            .format(self._db.quote(project_id))
        )

    def delete(self, project_id, ip):
        """ Delete IP from project """
        self._db.q(
            "DELETE FROM ips WHERE project_id = {0} AND ip = {1}"
            .format(self._db.quote(project_id), self._db.quote(ip))
        )
