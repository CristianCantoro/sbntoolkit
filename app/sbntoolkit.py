#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import Bottle
from bottle import run
from bottle import redirect
from bottle import static_file
from bottle import error
from bottle import template
from bottle import TEMPLATE_PATH
from bottle import request

import os
import logging
import math
from urlparse import urljoin

from code import retrieve_link, viaf_and_nosbn_in_itwiki

# logging
# logging
LOGFORMAT_STDOUT = {logging.DEBUG: '%(module)s:%(funcName)s:%(lineno)s - %(levelname)-8s: %(message)s',
                    logging.INFO: '%(levelname)-8s: %(message)s',
                    logging.WARNING: '%(levelname)-8s: %(message)s',
                    logging.ERROR: '%(levelname)-8s: %(message)s',
                    logging.CRITICAL: '%(levelname)-8s: %(message)s'
                    }

# --- root logger
rootlogger = logging.getLogger('sbnredirect')
rootlogger.setLevel(logging.DEBUG)

lvl_config_logger = logging.DEBUG

console = logging.StreamHandler()
console.setLevel(lvl_config_logger)

formatter = logging.Formatter(LOGFORMAT_STDOUT[lvl_config_logger])
console.setFormatter(formatter)

rootlogger.addHandler(console)

logger = logging.getLogger('sbnredirect.app')

# global
DOMAIN = 'http://baliststaging.es'

GITHUB = 'http://github.com/CristianCantoro'

WIKIPEDIA = 'http://{lang}.wikipedia.org/wiki/{page}'
WIKIDATA = 'http://www.wikidata.org/wiki/{item}'

TEMPLATE_PATH.append(os.path.join('app','views'))

SBNtoolkit = Bottle()

@SBNtoolkit.get('/')
def get_index(data=None):
  return static_file('index.html', root='app/static/')

@SBNtoolkit.route('/github')
def github():
    redirect(GITHUB)

@SBNtoolkit.route('/sbnt/css/<css_file>')
@SBNtoolkit.route('/css/<css_file>')
def serve_css(css_file):
  return static_file(css_file, root='app/static/css')

@SBNtoolkit.route('/sbnt/images/<filepath:path>')
@SBNtoolkit.route('/images/<filepath:path>')
def serve_images(filepath):
  return static_file(filepath, root='app/static/images')

@SBNtoolkit.route('/sbnt/js/<filepath:path>')
@SBNtoolkit.route('/js/<filepath:path>')
def serve_js(filepath):
  return static_file(filepath, root='app/static/js')

@SBNtoolkit.route('/favicon.ico')
def serve_favicon():
  return static_file('favicon.ico', root='app/static/')

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


@SBNtoolkit.get('/download')
@SBNtoolkit.get('/download/<filepath:path>')
def download(filepath=None):
    if filepath:
        redirect(urljoin(DOMAIN,'download/{}'.format(filepath)))
    else:
        redirect(urljoin(DOMAIN,'download'))

@SBNtoolkit.get('/list')
def get_list(filepath=None):

    p = request.query.get('p')

    logger.debug('p: {}'.format(p))

    page = 0
    try:
        if p:
            page = int(p) - 1
    except:
        logger.error(p)

    items_per_page = 500

    offset = page*items_per_page

    logger.debug('page: {}'.format(page))
    logger.debug('offset: {}'.format(offset))

    tot_items, items = viaf_and_nosbn_in_itwiki(offset=offset,
                                                        perpage=items_per_page
                                                       )


    item_list = []
    for item in items:
        code = item['viaf.code']
        page_id = item['viaf.page_id']
        item_id = item['viaf.data_id']
        wikipedia_link = WIKIPEDIA.format(lang='it',
                                   page=item['pages.title'].encode('utf-8')
                                  )
        wikipedia_title = '<a href="{link}">{title}</a>'.format(
                            link=wikipedia_link,
                            title=item['pages.title'].encode('utf-8')
                           )
        wikidata_link = WIKIDATA.format(item=item['data.title'])
        wikidata_title = '<a href="{link}">{title}</a>'.format(
                            link=wikidata_link,
                            title=item['data.title']
                           )
        linked = item['data.linked']

        item_list.append([code, page_id, wikidata_title,
                          wikipedia_title, item_id, linked])

    tot_pages = int(math.ceil(tot_items/float(items_per_page)))

    logger.debug('tot_pages: {}'.format(tot_pages))

    logger.debug(len(item_list))

    return template('list.tpl',
                    items=item_list,
                    active_page=page + 1,
                    tot_pages=tot_pages)

@error(404)
def error404(error):
    return 'Nothing here, sorry'

if __name__ == '__main__':

    logger.debug('test')

    if not os.path.isdir('app'):
        basedir = os.path.dirname(os.path.realpath(__file__))
        new_basedir = os.path.realpath(os.path.join(basedir,'..'))

        os.chdir(new_basedir)
        print 'new_basedir', new_basedir

    run(SBNtoolkit,host='0.0.0.0', port=39600, debug=True,reloader=True)