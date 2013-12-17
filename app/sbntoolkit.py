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
import re
import logging
import math
from urlparse import urljoin

from code import retrieve_link, viaf_and_nosbn_in_itwiki
from viafsbn import search_viaf, search_sbn

# logging
LOGFORMAT_STDOUT = {
    logging.DEBUG: '%(module)s:%(funcName)s:%(lineno)s - '
                   '%(levelname)-8s: %(message)s',
    logging.INFO: '%(levelname)-8s: %(message)s',
    logging.WARNING: '%(levelname)-8s: %(message)s',
    logging.ERROR: '%(levelname)-8s: %(message)s',
    logging.CRITICAL: '%(levelname)-8s: %(message)s'}

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
GITHUB = 'http://github.com/CristianCantoro/SBNtoolkit'

WIKIPEDIA = 'http://{lang}.wikipedia.org/wiki/{page}'
WIKIDATA = 'http://www.wikidata.org/wiki/{item}'

TEMPLATE_PATH.append(os.path.join('app', 'views'))

REGEXP = r'IT(\\|/)?ICCU(\\|/)?.*'

SBNtoolkit = Bottle()


@SBNtoolkit.get('/')
def get_index():
    return static_file('index.html', root='app/static/')


@SBNtoolkit.post('/')
def post_index():
    code = request.forms.get('code').strip()

    link_info = retrieve_link('it', 'sbn', code) or \
        retrieve_link('data', 'sbn', code)

    if link_info:
        logger.debug(link_info)
        page, res_type, linked = link_info

        if res_type == 'data':
            return template('sbn_to_wiki_via_data',
                            code=code,
                            page=page,
                            link=page.replace(' ', '_'),
                            item=linked
                            )
        else:
            return template('sbn_to_wiki',
                            code=code,
                            page=page,
                            link=page.replace(' ', '_')
                            )

    else:
        return template('code_not_found',
                        code=code,
                        tipo='SBN'
                        )


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

    def to_python(match):
        return match.replace('/', '\\')

    def to_url(string):
        return string

    return REGEXP, to_python, to_url

SBNtoolkit.router.add_filter('code', code_filter)


@SBNtoolkit.get('/hello/<code:code>')
def hello(code):
    return "Hello, {code}".format(code=code)


@SBNtoolkit.get('/get/<lang>/<code_type>/<code:code>')
@SBNtoolkit.get('/get/<lang>/sbn/<code:code>')
def get_page(lang, code, code_type='sbn'):
    link = retrieve_link(lang, code_type, code)
    if link_info:
        link, res_type, linked = link_info
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
    link_info = retrieve_link(lang, code_type, code)

    if link_info:
        link, res_type, linked = link_info
        link = link.encode('utf-8')
        if lang == 'data' or lang == 'wikidata':
            link = WIKIDATA.format(item=link)
        else:
            link = WIKIPEDIA.format(lang='it', page=link)

        redirect(link)
    else:
        return link_not_found(lang=lang,
                              code_type=code_type,
                              code=code
                              )


@SBNtoolkit.get('/list')
def get_list(filepath=None):

    p = request.query.get('p')
    #n = request.query.get('n')
    o = request.query.get('o')
    v = request.query.get('v')

    page = 0
    try:
        if p:
            page = int(p) - 1
    except:
        logger.error(p)

    n = 500
    items_per_page = 500
    try:
        if n:
            items_per_page = int(n)
    except:
        logger.error(n)

    order = None
    try:
        COLUMNS = ['viaf.code', 'data.title', 'pages.title']
        order = o in COLUMNS and o or None
    except:
        logger.error(o)

    direction = None
    try:
        DIRECTIONS = ['asc', 'desc']
        direction = v in DIRECTIONS and v or None
    except:
        logger.error(o)

    offset = page*items_per_page

    logger.debug('page: {}'.format(page))
    logger.debug('offset: {}'.format(offset))
    logger.debug('order: {}'.format(order))

    tot_items, items = viaf_and_nosbn_in_itwiki(offset=offset,
                                                perpage=items_per_page,
                                                order=order,
                                                direction=direction
                                                )

    item_list = []
    for item in items:
        code = item['viaf.code']
        page_id = item['viaf.page_id']
        item_id = item['viaf.data_id']
        wikipedia_link = WIKIPEDIA.format(
            lang='it',
            page=item['pages.title'].encode('utf-8')
        )
        wikipedia_title = '<a href="{link}">{title}</a>'.format(
            link=wikipedia_link,
            title=item['pages.title'].encode('utf-8')
        )
        wikidata_link = WIKIDATA.format(
            item='Q'+str(item['data.title'])
        )
        wikidata_title = '<a href="{link}">Q{title}</a>'.format(
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
                    order=order,
                    direction=direction,
                    tot_pages=tot_pages
                    )


@SBNtoolkit.get('/search/<code_type>/<code:code>')
@SBNtoolkit.get('/search/sbn/<code>')
def search(code, code_type='SBN'):
    pass


@SBNtoolkit.get('/viafsbn')
def get_viafsbn():
    return static_file('viafsbn.html', root='app/static/')


@SBNtoolkit.post('/viafsbn')
def post_viafsbn():
    code = request.forms.get('code').strip()

    item = None
    tipo = 'ERRORE'
    if re.match(REGEXP, code):
        tipo = 'SBN'
        code = code.replace('/', '\\')
        item = search_sbn(code)
    else:
        tipo = 'VIAF'
        item = search_viaf(code)

    if item:
        return template('viafsbn', item=item, tipo=tipo)
    else:
        return template('code_not_found', code=code, tipo=tipo)


@error(404)
def error404(error):
    return 'Nothing here, sorry'


if __name__ == '__main__':

    if not os.path.isdir('app'):
        basedir = os.path.dirname(os.path.realpath(__file__))
        new_basedir = os.path.realpath(os.path.join(basedir, '..'))

        os.chdir(new_basedir)
        print 'new_basedir', new_basedir

    app = Bottle()

    @app.get('/')
    @app.get('/sbnt')
    def app_index():
        return redirect('/sbnt/')
    app.mount(prefix='/sbnt/', app=SBNtoolkit)
    run(app, host='localhost', port=39600, debug=True, reloader=True)
