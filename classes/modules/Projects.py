# -*- coding: utf-8 -*-
""" Class of module Projects """

from classes.Registry import Registry
from classes.kernel.WSModule import WSModule
from classes.kernel.WSOption import WSOption
from classes.kernel.WSException import WSException
from classes.models.ProjectsModel import ProjectsModel


class Projects(WSModule):
    """ Class of module Projects """
    model = None
    log_path = '/dev/null'
    options = {}
    options_sets = {
        "add": {
            "descr": WSOption("descr", "Description of project", "", False, ['--descr'])
        },
        "list": {

        },
        "delete": {

        },
    }

    def __init__(self, kernel):
        WSModule.__init__(self, kernel)
        self.model = ProjectsModel()

    def list_action(self):
        """ Action list of module """
        print "{0:=^51}".format("")
        print "| {0: ^23}| {1: ^23}|".format('Title', 'Description')
        print "{0:=^51}".format("")
        for project in self.model.list():
            print "| {0: <23}| {1: <23}|".format(project['name'], project['descr'])
        print "{0:=^51}".format("")

    def delete_action(self):
        """ Delete action of module """
        name = Registry().get('project')
        answer = raw_input("You really want to delete project '{0}' [y/n]? ".format(name))
        if answer.lower() == 'y':
            self.model.delete(name)
            print "Project '{0}' successfully deleted.".format(name)
        else:
            print "Project '{0}' not deleted.".format(name)

    def add_action(self):
        """ Action add of module """
        name = Registry().get('project')
        if self.model.exists(name):
            raise WSException("Project with name '{0}' already exists!".format(name))
        self.model.create(name, self.options['descr'].value)
        print " Project '{0}' with description '{1}' successfully created! ".\
              format(name, self.options['descr'].value)

    def run(self, action):
        """ Method of run the module """
        WSModule.run(self, action)
        self.done = True
