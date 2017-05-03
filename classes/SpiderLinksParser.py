# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class for parse site content and extract link from it (and other wotks with links)
"""

import re
import copy
from urlparse import urlparse

from lxml import etree

from classes.Registry import Registry
from libs.common import validate_uri_start

class SpiderLinksParser(object):
    """ Class for parse site content and extract link from it (and other wotks with links) """
    tags = {}

    def __init__(self):
        self.tags = {}
        tags = Registry().get('config')['spider']['tags']
        tags = tags.split(",")
        for tag in tags:
            tag = tag.split("|")
            self.tags[tag[0]] = tag[1]

    def parse_links(self, content_type, content, link):
        """
        Method parse a page content and extract links from it. Can parse xml, html and css.
        Other content parse how plain text
        :param content_type: type of content (text/xml, application/xml, text/html, text/css or other one)
        :param content: content of page
        :param link: url of current page
        :return:
        """
        try:
            if not len(content.strip()):
                return []

            if content_type in ['text/xml', 'application/xml'] or content[:6] == '<?xml ':
                links = self.parse_links_xml(content)
                text_links = self.parse_links_text_re(content)
                links.extend(text_links)
            elif content_type == 'text/css':
                links = self.parse_links_css(content)
                text_links = self.parse_links_text_re(content)
                links.extend(text_links)
            elif content_type == 'text/html':
                links = self.parse_links_html_re(content)
                text_links = self.parse_links_text_re(content)
                links.extend(text_links)
            else:
                links = self.parse_links_html_re(content)
                text_links = self.parse_links_text_re(content)
                links.extend(text_links)

            if Registry().isset('ignore_regexp'):
                links = self._clear_ignore(links)

            if Registry().isset('only_one'):
                links = self._clear_only_one(links)

            if Registry().get('config')['spider']['denied_schemes']:
                links = self._clear_by_schema(links)

        except etree.XMLSyntaxError:
            links = self.parse_links_text_re(content)
            Registry().get('logger').log(
                " Document syntax error {0}, parsing as text"
                .format(link['path'] + '?' + link['query'] if len(link['query']) else link['path'])
            )
        except etree.DocumentInvalid:
            links = self.parse_links_text_re(content)
            Registry().get('logger').log(
                " Document invalid {0}, parsing as text"
                .format(link['path'] + '?' + link['query'] if len(link['query']) else link['path'])
            )

        return list(set(links))

    def parse_links_text_re(self, content):
        """ Method parse links from usual text """
        content = content.replace("]]>", "").replace("<![CDATA[", "")
        content = re.sub(r"<([/a-zA-Z:\-0-9]*?)>", " ", content)
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        urls = map(
            lambda url: url.strip('\'" ,);'),
            urls
        )
        return urls


    def parse_links_xml(self, content):
        """ Method parse links from xml """
        links = []
        tree = etree.XML(content, etree.XMLParser())
        tags = tree.xpath('//*')
        for tag in tags:
            if tag.text and validate_uri_start(tag.text):
                links.append(tag.text)

            for attr in tag.attrib:
                if validate_uri_start(tag.attrib[attr]):
                    links.append(tag.attrib[attr])

            if tag.text and tag.text.strip():
                try:
                    content_links = self.parse_links_html_re(tag.text)
                    links.extend(content_links)
                except KeyError:
                    Registry().get('logger').log("ENC: " + tag.text)

        return links

    def parse_links_css(self, content):
        """ Method parse links from css """
        links = re.findall(r':(?: |)url(?: |)\((.*?)\)', content)
        for link in links:
            if link[0] in ['"', '\'']:
                links[links.index(link)] = link[1:len(link)-1]
        return links

    def parse_links_html_re(self, content):
        """ Method parse links from html """
        content = content.replace('<', '\n<')
        to_return = []

        for tag in self.tags:
            to_return.extend(
                re.findall(r"<{0}(?:.*){1}=(?:'|)([^'\"]*?)(?:'| |>)".format(tag, self.tags[tag]), content)
            )
            to_return.extend(
                re.findall(r"<{0}(?:.*){1}=(?:\"|)([^'\"]*?)(?:\"| |>)".format(tag, self.tags[tag]), content)
            )

        return to_return

    def _clear_by_schema(self, links):
        """ Method clear links list from links with denied schema """
        denied_schemes = Registry().get('denied_schemes')

        result = []
        for link in links:
            parsed_link = urlparse(link)
            if not parsed_link.scheme or parsed_link.scheme not in denied_schemes:
                result.append(link)

        return result

    def _clear_ignore(self, links):
        """ Method clear links list from links matches ignore_regexp """
        original = copy.copy(links)
        for link in original:
            if link and Registry().get('ignore_regexp').search(link):
                links.remove(link)
        return links

    def _clear_only_one(self, links):
        """ Method clear links list from links matches only_one """
        original = copy.copy(links)
        for link in original:
            only_one = Registry().get('only_one')
            for rule in only_one:
                if re.search(rule['regex'], link):
                    if rule['block']:
                        links.remove(link)
                    else:
                        rule['block'] = True
            Registry().set('only_one', only_one)

        return links
