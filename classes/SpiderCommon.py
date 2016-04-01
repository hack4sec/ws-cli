# -*- coding: utf-8 -*-
""" Class with common functions for Spider module """

import copy
import time
import hashlib
import re
import os
import shutil
from urlparse import urlparse
from urlparse import ParseResult

import pymongo

from libs.common import md5, mongo_result_to_list
from classes.Registry import Registry
from classes.models.UrlsBaseModel import UrlsBaseModel
from classes.kernel.WSCounter import WSCounter
from classes.models.UrlsModel import UrlsModel
from classes.models.HostsModel import HostsModel


class SpiderCommon(object):
    """ Class with common functions for Spider module """
    _link_object = {
        'hash': '',
        'path': '',
        'query': '',
        'time': 0,
        'code':0,
        'checked': 0,
        'referer': '',
        'founder': '',
        'size': 0,
        'getted': 0
    }
    ignore_regexp = None
    _external_hosts = []
    denied_schemas = None

    @staticmethod
    def make_full_new_scan():
        """ Mark all links as no scanned """
        Registry().get('ndb').q("UPDATE urls SET spidered = 0")

    @staticmethod
    def _clear_link_obj(link):
        """ Clear dict with link data from excess parts """
        original = copy.copy(link)
        for item in original:
            if item not in SpiderCommon._link_object:
                del link[item]
        return link

    @staticmethod
    def links_checked(links):
        """ Mark links as checked """
        for link in links:
            link = SpiderCommon._clear_link_obj(link)
            link['checked'] = 1
            Registry().get('mongo').spider_urls.update({'hash': link['hash']}, {'$set': link})

    @staticmethod
    def gen_url(link, host):
        """ Generate URL by host and dict of link data """
        url = 'http://' + host + link['path']
        if link['query']:
            url += '?' +  link['query']
        return url

    @staticmethod
    def prepare_links_for_insert(links, url, site):
        """ Get links dicts and prepare it to insert in MongoDB """
        links_to_insert = []
        for link in links:
            if not link:
                continue

            link = urlparse(link)

            if not link.scheme and \
                not link.netloc and \
                not link.path and \
                not link.query:
                continue

            if link.netloc \
                and link.netloc != site \
                and 'www.' + link.netloc != site \
                and link.netloc != 'www.' + site:
                SpiderCommon._external_hosts.append(link.netloc)
                continue

            link = SpiderCommon.clear_link(link)
            link = SpiderCommon.build_path(link, url.path)
            link = SpiderCommon.clear_link(link)

            links_to_insert.append(link)

        separated_links = []
        for link in links_to_insert:
            paths = link.path.split("/")
            while len(paths) != 1:
                del paths[-1]
                separated_links.append(
                    ParseResult(
                        scheme='',
                        netloc='',
                        path="/".join(paths) + '/',
                        params='',
                        query='',
                        fragment=''
                    )
                )
        return links_to_insert + separated_links

    @staticmethod
    def get_denied_schemas():
        """ Get list of denied schemas """
        if SpiderCommon.denied_schemas is None:
            denied_schemas = Registry().get('config')['spider']['denied_schemes'].split(',')
            for dschema in denied_schemas:
                index = denied_schemas.index(dschema)
                denied_schemas[index] = dschema.encode('utf8')
            SpiderCommon.denied_schemas = list(map(str.strip, denied_schemas))
        return SpiderCommon.denied_schemas

    @staticmethod
    def get_url_hash(path, query):
        """ Build md5-hash for url """
        path = path.strip()
        query = query.strip()
        url = str(path + query).decode('utf-8', errors='ignore')
        #url = url.encode()
        return hashlib.md5(url.encode('utf-8')).hexdigest(),

    @staticmethod
    def insert_links(links, referer, site):
        """ Put links data in MongoDB """
        links = SpiderCommon.prepare_links_for_insert(links, urlparse(referer), site)
        if not len(links):
            return

        denied_schemas = SpiderCommon.denied_schemas

        for link in links:
            if 'scheme' in link and link['scheme'] in denied_schemas:
                continue

            insert = {
                'hash': SpiderCommon.get_url_hash(link.path, link.query),
                'path': link.path.strip(),
                'query': link.query.strip(),
                'referer': referer,
                'founder': 'spider',
                'checked': 0 if SpiderCommon._link_allowed(link) else 1,
                'getted': 0,
                'code': 0,
                'time': 0,
                'size': 0
            }

            try:
                Registry().get('mongo').spider_urls.insert(insert)
            except pymongo.errors.DuplicateKeyError:
                pass
            except BaseException as e:
                Registry().get('logger').log(
                    "Can`t insert link " + insert['path'] + " " + insert['query'] + ") in db. "
                    "May be it have non-utf8 symbols or somethink else. Exception message:"
                )
                Registry().get('logger').ex(e)

    @staticmethod
    def _link_allowed(link):
        """ Are link match to allow_regexp ? """
        return Registry().get('allow_regexp').search(link.path) if link.path[len(link.path)-5:].count('.') else True

    @staticmethod
    def build_path(link, url_path):
        """ Build link with full path (for relatively links) """
        if link.path[0:1] == '/':
            return link

        path = link.path
        path = SpiderCommon.del_file_from_path(url_path) + "/" + path

        return ParseResult(
            scheme=link.scheme,
            netloc=link.netloc,
            path=path,
            params=link.params,
            query=link.query,
            fragment=link.fragment
        )

    @staticmethod
    def del_file_from_path(path):
        """ Method delete file from path """
        if path.find("/") == -1:
            return ""

        path = path.split("/")

        if path[-1].find("."):
            del path[-1]

        if len(path) == 1 and not path[0]:
            return "/"

        return "/".join(path)

    @staticmethod
    def clear_link(link):
        """ Clear link from some trash """
        path = link.path
        while path and (path.find("\\") > -1 or path.find("//") > -1 or path.find("/./") > -1):
            path = path.replace("\\", "/")
            path = path.replace("//", "/")
            path = path.replace("/./", "/")

        query = link.query.replace('&amp;', '&') if link.query else ""

        back_regex = re.compile(r"(.*|)/(.*)/\.\./") #свойство
        reg_res = back_regex.findall(path)
        while reg_res and len(reg_res[0]) == 2:
            path = path.replace(reg_res[0][1] + "/../", "")
            reg_res = back_regex.findall(path)

        return ParseResult(
            scheme=link.scheme,
            netloc=link.netloc,
            path=path,
            params=link.params,
            query=query,
            fragment=link.fragment
        )

# ==============================================================
    _header_object = {'url': '', 'header': '', 'value': ''}
    _pages = []
    _sitemap_name = ''

    def get_link_data_by_hash(self, _hash):
        """ Return link data from MongoDB by hash """
        return Registry().get('mongo').spider_urls.find_one({'hash': _hash})

    @staticmethod
    def clear_old_data(host):
        """ Clear data from old scans of current host """
        Registry().get('mongo').spider_urls.drop()

        if os.path.exists(Registry().get('data_path') + host):
            shutil.rmtree(Registry().get('data_path') + host)

    def _get_pages_list(self, _map):
        """ Get list of pages with scan data of current host """
        expr = re.compile('^[a-z0-9]{32}$')
        if not len(self._pages):
            for page in os.listdir(Registry().get('data_path') + _map):
                if expr.match(page):
                    self._pages.append(page)

        return self._pages

    @staticmethod
    def prepare_first_pages(host):
        """ Prepare link on first page in MongoDB. Add root url if urls for this host not exists.  """
        pid = Registry().get('pData')['id']

        coll = Registry().get('mongo').spider_urls
        coll.drop()

        Urls = UrlsModel()
        urls = Urls.list_by_host_name_for_spider(pid, host)
        if not len(urls):
            Registry().get('logger').log("Spider: Root URL was added automaticaly")
            Urls.add(
                pid, HostsModel().get_id_by_name(pid, host), '/', who_add='spider'
            )
            urls = Urls.list_by_host_name_for_spider(pid, host)

        for url in urls:
            url = urlparse(url['url'])
            data = {
                'hash': md5(str(url.path + url.query)),
                'path': url.path,
                'query': url.query,
                'time': 0,
                'code':0,
                'checked': 0,
                'getted' : 0,
                'referer': '',
                'size': 0,
                'founder': 'spider'
            }

            coll.insert(data)

        coll.create_index([('hash', 1)], unique=True, dropDups=True)
        coll.create_index([('checked', 1)])


    @staticmethod
    def links_in_spider_base(pid, host):
        """ Put found links in MySQL """
        links_per_time_limit = 50
        c = WSCounter(1, 60, int(Registry().get('mongo').spider_urls.count()/links_per_time_limit))
        Urls = UrlsModel()
        host_id = HostsModel().get_id_by_name(pid, host)
        urls_add = []

        skip = 0
        while True:
            links = mongo_result_to_list(
                Registry().get('mongo').spider_urls.find().skip(skip).limit(links_per_time_limit)
            )

            for link in links:
                url = link['path'] + '?' + link['query'] if len(link['query']) else link['path']
                urls_add.append({
                    'url': url,
                    'referer': link['referer'],
                    'response_code': link['code'],
                    'response_time': link['time'],
                    'size': link['size'],
                    'who_add': 'spider',
                    'spidered': link['checked']
                })
            Urls.add_mass(pid, host_id, urls_add)

            urls_add = []

            to_update = {
                'spidered': [],
                'code': [],
                'time': [],
                'size': []
            }

            for link in links:
                url = link['path'] + '?' + link['query'] if len(link['query']) else link['path']
                if link['checked']:
                    to_update['spidered'].append({'url': url, 'value': 1})
                to_update['code'].append({'url': url, 'value': link['code']})
                to_update['time'].append({'url': url, 'value': link['time']})
                to_update['size'].append({'url': url, 'value': link['size']})

            Urls.update_url_field_mass(pid, host, 'spidered', to_update['spidered'])
            Urls.update_url_field_mass(pid, host, 'response_code', to_update['code'])
            Urls.update_url_field_mass(pid, host, 'response_time', to_update['time'])
            Urls.update_url_field_mass(pid, host, 'size', to_update['size'])

            skip += len(links)

            c.up()

            if len(links) < links_per_time_limit:
                break

    @staticmethod
    def links_in_urls_base(pid, host):
        """ Put links in url_base table (MySQL) for site tree build """
        links_per_time_limit = 50
        c = WSCounter(1, 60, Registry().get('mongo').spider_urls.count()/links_per_time_limit)
        UrlsBase = UrlsBaseModel()
        host_id = HostsModel().get_id_by_name(pid, host)

        skip = 0
        while True:
            links = mongo_result_to_list(
                Registry().get('mongo').spider_urls.find().skip(skip).limit(links_per_time_limit)
            )
            for link in links:
                url = link['path'] + '?' + link['query'] if len(link['query']) else link['path']
                UrlsBase.add_url(
                    host_id,
                    url
                )
            skip += len(links)
            c.up()

            if len(links) < links_per_time_limit:
                break

    @staticmethod
    def links_in_database(pid, host):
        """ Method for insert all found links in MySQL in work end """
        Registry().get('logger').log(
            "\nInsert links in DB..." + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
        SpiderCommon.links_in_spider_base(pid, host)
        Registry().get('logger').log(
            "\nInsert links in DB (base)..." + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
        SpiderCommon.links_in_urls_base(pid, host)
        #print "\nMysql Done " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
