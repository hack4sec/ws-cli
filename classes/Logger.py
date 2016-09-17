# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class for logging WS output
"""

import codecs
import sys
import re
import os
import traceback
import random

from libs.common import t, file_get_contents
from classes.Registry import Registry
from classes.kernel.WSException import WSException


class Logger(object):
    """ Class for logging WS output """
    logs_dir = None
    module_name = None
    log_fh = None
    items_dir = None

    def __init__(self, module_name, have_items):
        self.module_name = module_name
        logs_dir = "{0}/logs/{1}".format(Registry().get('wr_path'), module_name)
        curdate = t("%Y-%m-%d")
        curtime = t("%H_%M_%S")

        if not os.path.exists(logs_dir):
            raise WSException("LOGGER ERROR: Path {0} for module {1} not exists!".format(logs_dir, module_name))

        if not os.path.exists("{0}/{1}".format(logs_dir, curdate)):
            os.mkdir("{0}/{1}".format(logs_dir, curdate))

        if not os.path.exists("{0}/{1}/{2}".format(logs_dir, curdate, curtime)):
            os.mkdir("{0}/{1}/{2}".format(logs_dir, curdate, curtime))

        if have_items:
            self.items_dir = "{0}/{1}/{2}/items".format(logs_dir, curdate, curtime)
            os.mkdir(self.items_dir)

        self.logs_dir = "{0}/{1}/{2}".format(logs_dir, curdate, curtime)

        self.log_fh = open("{0}/run.log".format(self.logs_dir), "w")

    def log(self, _str, new_str=True, _print=True):
        """ Write string in log and print it if need """
        self.log_fh.write(
            (t("[%H:%M:%S] ") if new_str else '') + _str + ('\n' if new_str else '')
        )
        self.log_fh.flush()
        if _print:
            if new_str:
                print _str
            else:
                print _str,
        sys.stdout.flush()

    def item(self, name, content, binary=False):
        """ Write item and it content in txt-file """
        if int(Registry().get('config')['main']['log_modules_items']) and len(name):
            name = name[1:] if name[0] == '/' else name
            name = name.replace(" ", "_")
            name = re.sub(r"[^a-zA-Z0-9_\-\.\|]", "_", name)

            ext = "bin" if binary else "txt"
            #fh = open("{0}/{1}.{2}".format(self.items_dir, name, ext), 'wb')
            fh = codecs.open("{0}/{1}.{2}".format(self.items_dir, name, ext), 'wb', 'utf-8')
            #content = bytearray(content)
#            try:
#                fh.write(content)
#            except UnicodeDecodeError:
#                fh.write("ENCODING ERROR")
#            fh = open(
#                "{0}/{1}.{2}".format(self.items_dir, name, ext),
#                "wb" if binary else "w"
#            )

            if binary:
                try:
                    fh.write(content)
                except UnicodeDecodeError:
                    fh.write("BINARY ENCODING ERROR")
            else:
                decoded_content = ""
                for symbol in content:
                    try:
                        symbol = codecs.encode(symbol, 'utf8', 'ignore')
                    except UnicodeDecodeError:
                        symbol = '?'
                    decoded_content += symbol
                fh.write(decoded_content)
                #codecs.encode(content, 'utf8', 'ignore') - not work!
            fh.close()

    def ex(self, _exception):
        """ Log func for exceptions """

        # Very ugly hack, will be fixed
        tmp_file_name = "/tmp/{0}{1}.txt".format("wsexc", random.randint(1, 9999))
        fh = open(tmp_file_name, "w")
        traceback.print_stack(file=fh)
        fh.close()
        trace_text = file_get_contents(tmp_file_name)
        os.remove(tmp_file_name)

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        log_str = "Exception {1}:\n{2} ({3}): {4}\n{0}\n{5}{0}\n".format(
            "{0:=^20}".format(""),
            exc_type,
            fname,
            exc_tb.tb_lineno,
            str(_exception),
            trace_text,
        )

        self.log(log_str, _print=False)
