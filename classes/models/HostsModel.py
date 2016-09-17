# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class for work with hosts table
"""
from classes.models.IpsModel import IpsModel
from classes.models.CommonModel import CommonModel

class HostsModel(CommonModel):
    """ Class for work with hosts table """
    def get_id_by_name(self, project_id, name):
        """ Return host ID by project ID and hostname """
        return self._db.fetch_one(
            "SELECT id FROM hosts WHERE project_id = {0} AND name = {1}"
            .format(self._db.quote(project_id), self._db.quote(name))
        )

    def get_by_name(self, project_id, name):
        """ Return host data by project ID and hostname """
        return self._db.fetch_row(
            "SELECT id, name, ip_id, descr FROM hosts WHERE project_id = {0} AND name = {1}"
            .format(self._db.quote(project_id), self._db.quote(name))
        )

    def exists(self, project_id, name):
        """ Is hosts exists in current project? """
        return self._db.fetch_one(
            "SELECT 1 FROM hosts WHERE project_id = {0} AND name= {1}"
            .format(self._db.quote(project_id), self._db.quote(name))
        )

    def add(self, project_id, ip_id, name, descr='', founder=''):
        """ Add host to table """
        return self._db.insert(
            "hosts",
            {
                'project_id': project_id,
                'ip_id': ip_id,
                'name': name,
                'descr': descr,
                'founder': founder
            },
            1
        )

    def list(self, project_id, ip):
        """ Get list of hosts by project_id AND IPv4 """
        ip_id = IpsModel().get_id(project_id, ip)

        return self._db.fetch_all(
            "SELECT h.id, h.name, h.descr, i.ip FROM hosts h "
            "INNER JOIN ips i ON i.id = h.ip_id "
            "WHERE h.project_id = {0} AND i.id = {1} "
            "ORDER BY h.name ASC"
            .format(self._db.quote(project_id), self._db.quote(ip_id))
        )

    def list_without_ip(self, project_id):
        """ List of hosts by project ID """
        return self._db.fetch_all(
            "SELECT h.id, h.name, h.descr, i.ip FROM hosts h "
            "INNER JOIN ips i ON i.id = h.ip_id "
            "WHERE h.project_id = {0} "
            "ORDER BY h.name ASC"
            .format(self._db.quote(project_id))
        )

    def delete(self, project_id, name):
        """ Delete host from project """
        self._db.q(
            "DELETE FROM hosts WHERE project_id = {0} AND name = {1}"
            .format(self._db.quote(project_id), self._db.quote(name))
        )
