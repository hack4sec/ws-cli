# -*- coding: utf-8 -*-
""" Kernel class for module results """

class WSResult(object):
    results = []

    def put(self, item):
        """ Pu item to results """
        self.results.append(item)
        return self

    def as_string(self):
        """ Return results as string """
        result = ""
        for row in self.results:
            result += row + "\n"
        return result

    def get_all(self):
        """ Get list of all results """
        return self.results

    def unique(self):
        """ Remove dups from results list """
        self.results = list(set(self.results))
        return self
