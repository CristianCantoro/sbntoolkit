#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import Bottle
from bottle import run
from bottle import redirect
from bottle import static_file
from bottle import error
from bottle import template

from code import retrieve_link

GITHUB = 'http://github.com/CristianCantoro'

WIKIPEDIA = 'http://{lang}.wikipedia.org/wiki/{page}'
WIKIDATA = 'http://www.wikidata.org/wiki/{item}'

SBNtoolkit = Bottle()

@SBNtoolkit.get('/')
def get_index(data=None):
  return static_file('index.html', root='static/')

@SBNtoolkit.route('/github')
def github():
    redirect(GITHUB)

@SBNtoolkit.route('/css/<css_file>')
def serve_css(css_file):
  return static_file(css_file, root='static/css')

@SBNtoolkit.route('/images/<filepath:path>')
def serve_images(filepath):
  return static_file(filepath, root='static/images')

@SBNtoolkit.route('/favicon.ico')
def serve_favicon():
  return static_file('favicon.ico', root='static/')

@SBNtoolkit.route('/js/<filepath:path>')
def serve_js(filepath):
  return static_file(filepath, root='static/js')


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
    link = retrieve_link(lang, code)
    return link

def link_not_found(lang, code_type, code):
    if lang == 'data' or lang == 'wikidata':
        target = 'Wikidata'
    else:
        target = 'Wikipedia in Italiano'

    return template('link_not_found.tpl',
                    target=target,
                    code_type=code_type,
                    code=code
                   )

@SBNtoolkit.get('/redirect/<lang>/<code_type>/<code>')
@SBNtoolkit.get('/redirect/<lang>/sbn/<code:code>')
def redirect_sbn(lang, code, code_type='sbn'):
    link = retrieve_link(lang, code_type, code)

    if link:
        link = link.encode('utf-8')
        if lang == 'data' or lang == 'wikidata':
            link = WIKIDATA.format(item=link)
        else:
            link = WIKIPEDIA.format(lang='it',page=link)

        redirect(link)
    else:
        return link_not_found(lang=lang,
                              code_type=code_type,
                              code=code
                             )

@error(404)
def error404(error):
    return 'Nothing here, sorry'

if __name__ == '__main__':
    run(SBNtoolkit,host='sbnredirect.it', port=8080, debug=True,reloader=True)