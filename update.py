#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import requests
import os
import sys
from csvunicode import UnicodeWriter, UnicodeReader
import wikipedia_template_parser as wtp
from subprocess import Popen, PIPE

import database

WIKIPEDIA_OUTPUT = 'wp_pages.txt'
WIKIDATA_OUTPUT = 'wd_items.txt'
WIKIDATA_OUTPUT_TMP = 'tmp_wd_items.txt'
UPDATE_OUTPUT = 'items_to_update.txt'

FIELDS = ['lastrevid', 'pageid', 'title', 'counter', 'length',
          'contentmodel', 'pagelanguage', 'touched', 'ns']

OUT_FIELDS = FIELDS + ['source']

AVAILABLE_PROPERTIES = set(['P396', 'P214', 'P244'])

# logging
logger = logging.getLogger('sbnredirect.item')

# https://www.wikidata.org/w/api.php?\
# action=query\
# generator=backlinks
# gbltitle=Property:P396
# prop=info
# gbnamespace=0
def get_items_with_property(prop, gblcontinue=None):
    """
    Given a page title and the language returns page info of the latest
    revision of the page
    """
    url = 'http://www.wikidata.org/w/api.php'

    params = {
        'action': 'query',
        'generator': 'backlinks',
        'prop': 'info',
        'gbltitle': 'Property:{}'.format(prop),
        'gblnamespace': 0,
        'redirects': True,
        'gbllimit': 500,
        'format': 'json'
    }

    if gblcontinue:
        params['gblcontinue'] = gblcontinue

    res = requests.get(url, params=params)

    if not res.ok:
        res.raise_for_status()

    pages = res.json()['query']['pages']
    result = [pages[page] for page in pages]

    try:
        gblcontinue = res.json()['query-continue']['backlinks']['gblcontinue']
    except KeyError:
        gblcontinue = None

    if gblcontinue:
        result += get_items_with_property(prop, gblcontinue)

    return result

def get_items_to_update(table, items):
    logger.debug('no. of items: {no}'.format(no=len(items)))

    items_to_get = []
    for item in items:
        item['source'] = table
        data = database.query(table, item['pageid'])
        if data is None:
            items_to_get.append(item)
        else:
            if data['id'] != item['pageid']:
                touched = __touched(item['touched'])
                if touched > data['touched']:
                    items_to_get.append(item)

    return items_to_get

def get_wikidata_items_from_database(properties):
    try:
        pass
    except Exception as e:
        logger.error(e)

    return None

def _write_wikidata_file_header():
    if not os.path.isfile(WIKIDATA_OUTPUT) or \
           os.stat(WIKIDATA_OUTPUT).st_size == 0:
        with open(WIKIDATA_OUTPUT, 'w') as out:
            writer = UnicodeWriter(out)
            keys = [unicode(k) for k in FIELDS]
            writer.writerow(keys)
            out.flush()

def _write_wikidata_file_items(items):    
    with open(WIKIDATA_OUTPUT, 'a') as out:
        writer = UnicodeWriter(out)
        for item in items:
            row = [unicode(item[k]) for k in FIELDS]
            writer.writerow(row)
        out.flush()

def _get_property(p):
    if p in AVAILABLE_PROPERTIES:
        logger.debug('Get property {} from API'.format(p))
        items = None
        try:
            items = get_items_with_property(p)
        except Exception as e:
            logger.error(e)

        if items:
            logger.debug('Writing results for {}'.format(p))
            _write_wikidata_file_header()
            _write_wikidata_file_items(items)


def get_wikidata_items_from_api(properties):

    if properties:
        for p in properties:
            _get_property(p)

    # FIXME
    # lots of bugs in I/O
    p1 = Popen(['sort','-r', WIKIDATA_OUTPUT, '-o', WIKIDATA_OUTPUT_TMP],
               shell=True)
    p2 = Popen(['uniq', WIKIDATA_OUTPUT_TMP, WIKIDATA_OUTPUT],
               shell=True)

def get_wikidata_items(properties):
    items = []

    logger.debug('Try DB')

    items = get_wikidata_items_from_database(properties)
    
    if not items:
        logger.debug('Try API')
        get_wikidata_items_from_api(properties)


def __touched(touched):
    return int(touched.replace('-','').replace(':','')\
                .replace('T','').replace('Z',''))


def get_wikipedia_pages_from_database():
    try:
        raise Exception
    except Exception as e:
        logger.error(e)

    return None

def get_wikipedia_pages_from_api():
    pages = []

    try:
        pages = wtp.pages_with_template(
                    "Template:Controllo_di_autorità",
                    lang="it",
                    props=True
                )
    except Exception as e:
        logger.error(e)

    return pages

def get_wikipedia_pages():

    logger.debug('Try DB')
    pages = get_wikipedia_pages_from_database()
    
    if not pages:
        logger.debug('Try API')
        pages = get_wikipedia_pages_from_api()

    if pages:
        with open(WIKIPEDIA_OUTPUT, 'w') as out:
            writer = UnicodeWriter(out)
            keys = [unicode(k) for k in FIELDS]
            writer.writerow(keys)
            for page in pages:
                p = [unicode(page[k]) for k in keys]
                writer.writerow(p)

def drop(filename):
    proc = Popen(["rm", filename], stderr=PIPE)
    status = proc.wait()

    if status == 0:
        logger.info("Removed file {}".format(filename))
    else:
        output = proc.stderr.read()
        logger.error("rm exited with status: {}".format(status))
        logger.error(output)


def get_items(pedia=False, data=False, properties=None):
    if pedia:
        get_wikipedia_pages()

    if data:
        get_wikidata_items(properties)

def get_all_items_to_update(items=None):

    items_to_update = []

    wikipedia_pages = []
    wikidata_items = []
    if items:
        wikipedia_pages = [i for i in items if i['source'] == 'wikipedia']
        wikidata_items = [i for i in items if i['source'] == 'wikidata']
    else:
        try:
            with open(WIKIPEDIA_OUTPUT, 'r') as wpin:
                reader = UnicodeReader(wpin)
                wikipedia_pages = \
                    [dict(zip(FIELDS, r)) for r in reader][1:]
        except Exception as e:
            logger.error(e)

        try:
            with open(WIKIDATA_OUTPUT, 'r') as wdin:
                reader = UnicodeReader(wdin)
                wikidata_items = \
                    [dict(zip(FIELDS, r)) for r in reader][1:]
        except Exception as e:
            logger.error(e)

    wikipedia_pages_to_update = \
        get_items_to_update('pages', wikipedia_pages)

    wikidata_items_to_update = \
        get_items_to_update('data', wikidata_items)

    items_to_update = wikipedia_pages_to_update + wikidata_items_to_update

    return items_to_update

def read_items_to_update(filename=None):
    
    update_filename = filename
    if filename is None:
        update_filename = UPDATE_OUTPUT

    items_to_update = []

    if not os.path.isfile(update_filename) or \
            os.stat(update_filename).st_size == 0:
        get_items(pedia=True, data=True)
        items_to_update = get_all_items_to_update()

    try:
        with open(update_filename, 'r') as upin:
            reader = UnicodeReader(upin)

            items_to_update = [dict(zip(OUT_FIELDS, r)) for r in reader][1:]

            # dedup list
            # dl = [dict(zip(OUT_FIELDS, r)) for r in reader][1:]            
            # items_to_update = [dict(t) 
            #                    for t in set([tuple(d.items()) for d in dl])
            #                   ]

    except Exception as e:
        logger.error(e)

    return items_to_update

if __name__ == '__main__':
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

    parser = argparse.ArgumentParser(description='Update routines.')
    parser.add_argument('--drop', action='store_true',
                        help='Drop {wp} and {wd} and exits'.format(
                            wp=WIKIPEDIA_OUTPUT,
                            wd=WIKIDATA_OUTPUT
                           )
                       )
    parser.add_argument('--pedia', '-p', action='store_true',
                       help='Get Wikipedia pages')
    parser.add_argument('--data', '-d', action='store_true',
                       help='Get Wikidata items')
    parser.add_argument('--properties', '-r', action='append',
                       help='Wikidata properties to get (implies --data)')

    args = parser.parse_args()
    print args

    # print
    # items = get_items_with_property('P396')
    # # print items
    # del items
    # print

    if args.drop:
        drop(WIKIPEDIA_OUTPUT)
        drop(WIKIDATA_OUTPUT)
        drop(UPDATE_OUTPUT)
        sys.exit(0)

    if args.properties:
        args.data = True

    get_items(args.pedia, args.data, args.properties)

    items_to_update = get_all_items_to_update()

    with open(UPDATE_OUTPUT, 'w') as out:
        writer = UnicodeWriter(out)
        keys = [unicode(k) for k in OUT_FIELDS]
        writer.writerow(keys)
        for item in items_to_update:
            row = [unicode(item[k]) for k in keys]
            writer.writerow(row)
