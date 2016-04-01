# -*- coding: utf-8 -*-
""" Class for work with projects table """

from classes.models.CommonModel import CommonModel

class ProjectsModel(CommonModel):
    """ Class for work with projects table """
    def get_by_name(self, name):
        """ Get project data by project name """
        return self._db.fetch_row("SELECT id, name, descr FROM projects WHERE name = {0}".format(self._db.quote(name)))

    def exists(self, name):
        """ Is project exists? """
        return self._db.fetch_one(
            "SELECT 1 FROM projects WHERE name = {0}".format(self._db.quote(name))
        )

    def delete(self, name):
        """ Delete project by name """
        self._db.q(
            "DELETE FROM projects WHERE name = {0}".format(self._db.quote(name))
        )

    def create(self, name, descr):
        """ Add project to DB """
        return self._db.insert("projects", {"name": name, "descr": descr})

    def list(self):
        """ List of projects """
        return self._db.fetch_all("SELECT * FROM projects ORDER BY id ASC")
