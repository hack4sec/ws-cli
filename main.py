#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)
          (c) Alexey Meshcheryakov <tank1st99@gmail.com>

Main run file
"""

import sys
import argparse
import time
import logging

from libs.common import secs_to_text, main_help

from classes.kernel.WSBase import WSBase
from classes.Registry import Registry
from classes.kernel.WSException import WSException
from classes.models.ProjectsModel import ProjectsModel
from classes.Logger import Logger

if len(sys.argv) < 4:
    main_help()

project = sys.argv[1]
module_name = sys.argv[2]
action = sys.argv[3]

base = WSBase()

logging.captureWarnings(True)

try:
    module = base.load_module(module_name)
except WSException:
    print " ERROR: Module '{0}' not exists!".format(module_name)
    exit(0)

if module.logger_enable:
    Registry().set('logger', Logger(module.logger_name, module.logger_have_items))

if module.time_count:
    print "Started module work at " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start_time = int(time.time())

try:
    module.prepare(action)
except WSException as e:
    print " " + str(e)
    exit(0)

Projects = ProjectsModel()
if not Projects.exists(project) and action not in ('add', 'list'):
    print " ERROR: Project '{0}' not exists!".format(project)
    exit(0)

Registry().set('project', project)
Registry().set('pData', Projects.get_by_name(project))
Registry().set('module', module)
Registry().set('action', action)

parser = argparse.ArgumentParser(
    description=module.help(),
    prog="{0} {1} {2} {3}".format(sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3])
)
for option in module.options:
    parser.add_argument(
        *module.options[option].flags,
        required=module.options[option].required,
        help=module.options[option].description,
        dest=module.options[option].name
    )

args = vars(parser.parse_args(sys.argv[4:]))
for option in args.keys():
    if args[option] is not None:
        module.options[option].value = args[option].strip()

try:
    module.run(action)

    while not module.finished():
        try:
            sys.stdout.flush()
        except BaseException:
            time.sleep(1)

except WSException as e:
    print " " + str(e)

Http = Registry().get('http')
for k in Http.errors:
    for err_str in Http.errors[k]:
        print err_str

Registry().get('ndb').close()
if Registry().isset('display'):
    Registry().get('display').stop()

if module.time_count:
    print "\nEnded module work at " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print "Common work time: {0}".format(secs_to_text(int(time.time()) - start_time))
