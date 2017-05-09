# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for SpiderLinksParser
"""

import re

import pytest

from Common import Common
from classes.SpiderLinksParser import SpiderLinksParser
from classes.Registry import Registry


class Test_SpiderLinksParser(Common):
    """Unit tests for SpiderLinksParser"""
    def setup(self):
        self.model = SpiderLinksParser()

        Registry().set('denied_schemes', ['mailto', 'javascript'])
        Registry().set('allow_regexp', re.compile(''))


    full_links_data = [
        (
            'text/xml',
            '<?xml version="1.0" encoding="UTF-8"?><urls><url>http://link1.com</url>'
            '<url attr="https://link3.com/">http://link2.com</url></urls>',
            ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        ),
        (
            'application/xml',
            '<?xml version="1.0" encoding="UTF-8"?><urls><url>http://link1.com</url>'
            '<url attr="https://link3.com/">http://link2.com</url></urls>',
            ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        ),
        (
            'text/html',
            '<html><img src=\'http://link1.com\' some/>\n<a href="http://link2.com">link2</a>'
            '<form action="https://link3.com/">...</form></html>',
            ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        ),
        (
            'text/text',
            'I have some links http://link1.com and \nhttp://link2.com, and it`s good. But https://link3.com/ need',
            ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        ),
        (
            'text/css',
            '\tbody {\n\tbackground-image: url(http://link1.com);\n\tbackground-color: #c7b39b;\n\t}\n\n\t'
            'body {\n\tbackground-image: url(http://link2.com);\n\tbackground-color: #c7b39b;\n\t}/* '
            'Get from https://link3.com/ */\n\n',
            ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        ),
    ]

    @pytest.mark.parametrize("content_type,content,expected_links", full_links_data)
    def test_parse_links(self, content_type, content, expected_links):
        assert self.model.parse_links(content_type, content, '/') == expected_links


    text_links_data = [
        (
            '<?xml version="1.0" encoding="UTF-8"?><urls><url>http://link1.com</url>'
            '<url>http://link2.com</url>\n<url>https://link3.com/</url></urls>',
            ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        ),
        (
            '<html><img src=\'http://link1.com\' some/>\n<a href="http://link2.com">link2</a><'
            'form action="https://link3.com/">...</form></html>',
            ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        ),
        (
            'I have some links http://link1.com and \nhttp://link2.com, and it`s good. But https://link3.com/ need',
            ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        ),
    ]

    @pytest.mark.parametrize("content,expected_links", text_links_data)
    def test_parse_links_text(self, content, expected_links):
        assert self.model.parse_links_text_re(content) == expected_links


    html_links_data = [
        (
            '<html>\n\t<img src=\'http://link1.com\' some/>\n<a href="http://link2.com">link2</a>'
            '\n\t<form action="https://link3.com/">\n...\n</form>\n</html>',
            ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        ),
        (
            '<html><img src=\'http://link1.com\' some/><a href="http://link2.com">link2</a>'
            '<form action="https://link3.com/">...</form></html>',
            ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        ),
    ]

    @pytest.mark.parametrize("content,expected_links", text_links_data)
    def test_parse_links_html(self, content, expected_links):
        assert self.model.parse_links_text_re(content) == expected_links


    xml_links_data = [
        (
            '<?xml version="1.0" encoding="UTF-8"?><urls><url>http://link1.com</url>'
            '<url attr="https://link3.com/">http://link2.com</url></urls>',
            ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        ),
        (
            '<?xml version="1.0" encoding="UTF-8"?><urls><url><![CDATA[http://link1.com]]></url>'
            '<url><![CDATA[http://link2.com]]></url></urls>',
            ['http://link1.com', 'http://link2.com']
        ),
        (
            '<?xml version="1.0" encoding="UTF-8"?><urls><url><![CDATA[<a href="http://link1.com">link1</a>]]>'
            '</url>\n<url><![CDATA[<iframe src="http://link2.com">]]></url></urls>',
            ['http://link1.com', 'http://link2.com']
        ),
    ]

    @pytest.mark.parametrize("content,expected_links", xml_links_data)
    def test_parse_links_xml(self, content, expected_links):
        assert self.model.parse_links_xml(content) == expected_links


    css_links_data = [
        (
            '\tbody {\n\tbackground-image: url(http://link1.com);\n\tbackground-color: #c7b39b;\n\t}\n\n\t'
            '.class {\n\tbackground-image: url(http://link2.com);\n\tbackground-color: #c7b39b;\n\t}\n\t'
            '.class {\n\tbackground-image: url(https://link3.com/);\n\tbackground-color: #c7b39b;\n\t}\n\n',
            ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        ),
        (
            'body {background-image: url(http://link1.com);background-color: #c7b39b;}'
            '.class {background-image: url(http://link2.com);background-color: #c7b39b;}'
            '.class {background-image: url(https://link3.com/);background-color: #c7b39b;}',
            ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        ),
    ]
    @pytest.mark.parametrize("content,expected_links", css_links_data)
    def test_parse_links_css(self, content, expected_links):
        assert self.model.parse_links_css(content) == expected_links

    def test_clear_by_schema(self):
        in_links = [
            'http://link1.com', 'mailto:a@bbb.com', 'javascript:alert(2)',
            'http://link2.com', 'https://link3.com/', 'mailto:a@b.com', 'javascript:alert(1)',
        ]
        out_links = ['http://link1.com', 'http://link2.com', 'https://link3.com/']
        assert self.model._clear_by_schema(in_links) == out_links

    def test_clear_ignore(self):
        in_links = ['http://link1.com', 'http://link3.com/123', 'http://link2.com', 'https://link3.com/']
        out_links = ['http://link1.com', 'http://link2.com']
        Registry().set('ignore_regexp', re.compile('link3'))
        assert self.model._clear_ignore(in_links) == out_links

    def test_clear_only_one(self):
        in_links = ['http://link1.com', 'http://link1.com/123', 'http://link2.com',
                    'http://link2.com/123', 'https://link3.com/', 'http://link3.com/123']
        out_links = ['http://link1.com', 'http://link1.com/123', 'http://link2.com', 'https://link3.com/']
        Registry().set('only_one', [
            {'regex': 'link3', 'block': False},
            {'regex': 'link2', 'block': False}
        ])
        assert self.model._clear_only_one(in_links) == out_links
