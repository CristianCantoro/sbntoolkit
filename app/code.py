#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import database

# logging
logger = logging.getLogger('sbnredirect.app.code')

# global
TABLES = ['viaf', 'sbn', 'lccn']

IDS = {
'data': 'data_id',
'pages': 'page_id'
}

WIKIPEDIA = 'http://{lang}.wikipedia.org/wiki/{page}'

WIKIDATA = 'http://www.wikidata.org/wiki/{item}'


def retrieve_page_(lang, code_type, code):
    if lang == 'data' or lang == 'wikidata':
        page = 'Q1'
    else:
        page = 'Alessandro_Manzoni'
    return page

def retrieve_link(lang, code_type, code):
    if lang == 'data' or lang == 'wikidata':
        res_type = 'data'
        other_type = 'pages'
    else:
        res_type = 'pages'
        other_type = 'data'

    code = code.replace('/','\\')

    ids = database.query_code(code_type, code)

    if ids and ids[IDS[res_type]]:
        return database.retrieve_from(code_type, res_type, code)['title']
    else:
        retrieve = database.retrieve_from(code_type, other_type, code)
        if retrieve:
            linked = retrieve['linked']
            if linked:
                return database.query_id(res_type, linked)['title']

def viaf_and_nosbn_in_itwiki(offset=None, perpage=None):
    fields = ('viaf.code',
              'viaf.page_id',
              'viaf.data_id',
              'data.title',
              'data.linked',
              'pages.title'
             )

    if not isinstance(offset, int):
        offset = 0

    if not isinstance(perpage, int):
        perpage = 500

    query = """
            SELECT {fields}
            FROM viaf, data, pages
            WHERE data.id = viaf.data_id
                AND viaf.data_id NOT NULL
                AND data.linked NOT NULL
                AND viaf.data_id NOT IN
                    (SELECT DISTINCT sbn.data_id
                     FROM sbn
                     WHERE data_id NOT NULL)
                AND pages.id = data.linked
            LIMIT {perpage}
            OFFSET {offset}
            """.format(fields=', '.join(fields),
                       offset=offset,
                       perpage=perpage
                      )

    data = database.query(query)

    items = [dict(zip(fields, d)) for d in data]

    query = """
            SELECT count(*)
            FROM viaf, data, pages
            WHERE data.id = viaf.data_id
                AND viaf.data_id NOT NULL
                AND data.linked NOT NULL
                AND viaf.data_id NOT IN
                    (SELECT DISTINCT sbn.data_id
                     FROM sbn
                     WHERE data_id NOT NULL)
                AND pages.id = data.linked
            """.format(fields=', '.join(fields))

    res = database.query(query)

    tot = 0
    try:
        tot = res[0][0]
    except:
        pass

    items = tot, [dict(zip(fields, d)) for d in data]


    # import pdb
    # pdb.set_trace()

    return items


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

    print
    # print retrieve_page('data', '123')
    print
    print r"database.query_code('viaf', r'64167806')"
    print database.query_code('viaf', r'64167806')
    print
    print r"database.query_code('sbn', r'IT\ICCU\CFIV\016221')"
    print database.query_code('sbn', r'IT\ICCU\CFIV\016221')
    print
    print r"database.retrieve_from('sbn', 'data', r'IT\ICCU\CFIV\016221')"
    print database.retrieve_from('sbn', 'data', r'IT\ICCU\CFIV\016221')
    print
    print r"retrieve_link('data', 'sbn', r'IT\ICCU\CFIV\016221')"
    print retrieve_link('data', 'sbn', r'IT\ICCU\CFIV\016221')
    print
    print r"retrieve_link('it', 'sbn', r'IT\ICCU\MUSV\014924')"
    print r"--> database.retrieve_from('sbn', 'data', r'IT\ICCU\MUSV\014924')"
    print '--> ', database.retrieve_from('sbn', 'data', r'IT\ICCU\MUSV\014924')
    print retrieve_link('it', 'sbn', r'IT\ICCU\MUSV\014924')
    print
    print r"retrieve_link('it', 'sbn', r'IT\ICCU\CFIV\016221')"
    print retrieve_link('it', 'sbn', r'IT\ICCU\CFIV\016221')