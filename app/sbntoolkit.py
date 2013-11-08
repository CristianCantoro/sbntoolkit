#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import Bottle
from bottle import run
from bottle import redirect
from bottle import request
from bottle import response
from bottle import static_file, template
from urlparse import urlparse, parse_qs
import os
import re

from code import retrieve_page

GITHUB = 'http://github.com/CristianCantoro'

WIKIPEDIA = 'http://{lang}.wikipedia.org/wiki/{page}'
WIKIDATA = 'http://www.wikidata.org/wiki/{item}'

SBNtoolkit = Bottle()

@SBNtoolkit.get('/')
def get_index(data=None):
  return static_file('index.html', root='../static/')

@SBNtoolkit.route('/github')
def github():
    redirect(GITHUB)

@SBNtoolkit.route('/css/<css_file>')
def serve_css(css_file):
  return static_file(css_file, root='../static/css')

@SBNtoolkit.route('/images/<filepath:path>')
def serve_images(filepath):
  return static_file(filepath, root='../static/images')

@SBNtoolkit.route('/favicon.ico')
def serve_favicon():
  return static_file('favicon.ico', root='../static/')

@SBNtoolkit.route('/js/<filepath:path>')
def serve_js(filepath):
  return static_file(filepath, root='../static/js')


def code_filter(config):
    ''' Matches a IT\ICCU\ code'''

    regexp = r'IT(\\|/)?ICCU(\\|/)?.*'

    def to_python(match):
        return match.replace('/','\\')

    def to_url(string):
        return string

    return regexp, to_python, to_url

SBNtoolkit.router.add_filter('code', code_filter)

@SBNtoolkit.get('/hello/<code:code>')
def hello(code):
  return "Hello, {code}".format(code=code)

@SBNtoolkit.get('/get/<lang>/<code:code>')
def get_page(lang, code):
    page = retrieve_page(lang, code)
    return page

@SBNtoolkit.get('/redirect/<lang>/<code:code>')
def redirect_sbn(lang, code):

    if lang == 'data' or lang == 'wikidata':
        page = retrieve_page(lang, code)
        redirect(WIKIDATA.format(item=page))

    else:
        lang = 'it'

        page = retrieve_page(lang, code)

        redirect(WIKIPEDIA.format(
            lang=lang,
            page=page
            )
        )

if __name__ == '__main__':
    run(SBNtoolkit,host='sbnredirect.it', port=8080, debug=True,reloader=True)