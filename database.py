#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import sqlite3 as sqlite
from subprocess import Popen, PIPE


# logging
logger = logging.getLogger('sbnredirect.database')


# global
DBNAME = 'sbnredirect.db'
DBPATH = os.path.realpath(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '..', 'app'))

DATABASE = os.path.join(DBPATH, DBNAME)

logger.debug(DATABASE)


def _quote(string):
    if isinstance(string, str) or isinstance(string, unicode):
        string = string.replace("'", "''")
    return "'{}'".format(string)


def create():
    con = sqlite.connect(DATABASE)

    try:
        with con:
            cur = con.cursor()
            cur.execute("""CREATE TABLE
                           sbn(code TEXT PRIMARY KEY,
                               page_id BIGINT,
                               data_id BIGINT
                              )
                        """)
            cur.execute("""CREATE TABLE
                           viaf(code INT PRIMARY KEY,
                                page_id BIGINT,
                                data_id BIGINT
                               )
                        """)
            cur.execute("""CREATE TABLE
                           lccn(code TEXT PRIMARY KEY,
                                page_id BIGINT,
                                data_id BIGINT
                               )
                        """)
            cur.execute("""CREATE TABLE
                           Pages(id BIGINT PRIMARY KEY,
                                 title TEXT,
                                 touched BIGINT,
                                 latest BIGINT,
                                 linked BIGINT)
                        """)
            cur.execute("""CREATE TABLE
                           Data(id BIGINT PRIMARY KEY,
                                title INT,
                                touched BIGINT,
                                latest BIGINT,
                                linked BIGINT)
                        """)
    except sqlite.OperationalError as error:
        logger.error(error)


def drop():
    proc = Popen(["rm", DATABASE], stderr=PIPE)
    status = proc.wait()

    if status == 0:
        logger.info("Removed database {}".format(DATABASE))
    else:
        output = proc.stderr.read()
        logger.error("rm exited with status: {}".format(status))
        logger.error(output)


def write_codes(code_name, code_value, pageid=None, dataid=None):

    # logger.debug('value: %s' %(code_value and (page or data)) )
    if code_value and (pageid or dataid):
        con = sqlite.connect(DATABASE)

        query = None
        if pageid:
            query = """INSERT OR REPLACE INTO
                        {code_name}(code,
                                    page_id,
                                    data_id
                                   )
                        VALUES('{code_value}',
                                {page_id},
                               (SELECT data_id
                                FROM {code_name}
                                WHERE code = '{code_value}')
                              )
                    """.format(code_name=code_name,
                               code_value=code_value,
                               page_id=pageid and _quote(pageid) or 'NULL'
                               )

        if dataid:
            query = """INSERT OR REPLACE INTO
                        {code_name}(code,
                                    page_id,
                                    data_id
                                   )
                        VALUES('{code_value}',
                               (SELECT page_id
                                FROM {code_name}
                                WHERE code = '{code_value}'),
                                {data_id}
                              )
                    """.format(code_name=code_name,
                               code_value=code_value,
                               data_id=dataid and _quote(dataid) or 'NULL'
                               )

        if query:

            try:
                with con:
                    cur = con.cursor()
                    cur.execute(query)
            except Exception as e:
                logger.error("Insertion of codes into table {code_name} "
                             "failed".format(code_name=code_name))
                logger.error(query)
                logger.error(e)


def write_info(page, data):
    con = sqlite.connect(DATABASE)

    sources = {'Pages': page, 'Data': data}

    for s in sources:
        datum = sources[s]
        # logger.debug('{s}: {datum}'.format(s=s, datum=datum))
        if datum:

            linked = None
            if s == 'Pages':
                linked = data and data['pageid']
            else:
                linked = page and page['pageid']
                title = datum['title'].replace('Q', '')

            query = """INSERT OR REPLACE INTO
                            {table}(id,
                                    title,
                                    touched,
                                    latest,
                                    linked
                                   )
                            VALUES({id},
                                   {title},
                                   {touched},
                                   {latest},
                                   {linked}
                                  )
                    """.format(table=s,
                               id=datum['pageid'] or 'NULL',
                               title=_quote(datum['title'].encode('utf-8'))
                               or 'NULL',
                               touched=datum['touched'] or 'NULL',
                               latest=datum['lastrevid'] or 'NULL',
                               linked=linked or 'NULL'
                               )
            try:
                with con:
                    cur = con.cursor()
                    cur.execute(query)
            except Exception as e:
                logger.error("Insertion into {table} failed".format(table=s))
                logger.error(query)
                logger.error(e)


def query_id(table, page_id):
    fields = ("id", "title", "touched", "latest")
    con = sqlite.connect(DATABASE)

    query = """SELECT {fields}
               FROM {table}
               WHERE id = '{page_id}'
            """.format(fields=', '.join(fields),
                       table=table,
                       page_id=page_id)

    # logger.debug(query)
    data = None
    try:
        with con:
            cur = con.cursor()
            cur.execute(query)
            data = cur.fetchone()
    except Exception as e:
        logger.error("Retrieval of id {page_id} from table {table} failed"
                     .format(page_id=page_id, table=table))
        logger.error(query)
        logger.error(e)

    if data:
        data = dict(zip(fields, data))

    return data


def query_code(codename, code):
    fields = ("code", "page_id", "data_id")
    con = sqlite.connect(DATABASE)

    query = """SELECT {fields}
               FROM {table}
               WHERE code = '{code}'
            """.format(fields=', '.join(fields),
                       table=codename,
                       code=code
                       )

    # logger.debug(query)
    data = None
    try:
        with con:
            cur = con.cursor()
            cur.execute(query)
            data = cur.fetchone()
    except Exception as e:
        logger.error("Retrieval of code {code} from table {table} failed"
                     .format(code=code, table=codename))
        logger.error(query)
        logger.error(e)

    if data:
        data = dict(zip(fields, data))

    return data


def query(query):
    con = sqlite.connect(DATABASE)

    # logger.debug(query)
    data = None
    try:
        with con:
            cur = con.cursor()
            cur.execute(query)
            data = cur.fetchall()
    except Exception as e:
        logger.error("Execution of query failed.")
        logger.error(query)
        logger.error(e)

    return data


def retrieve_from(code_type, res_type, code):
    fields = ('code', 'page_id', 'data_id', 'title', 'linked')
    con = sqlite.connect(DATABASE)

    if res_type == 'data':
        res_type_id = 'data_id'
    else:
        res_type_id = 'page_id'

    query = """SELECT {fields}
               FROM {code_type}, {res_type}
               WHERE {res_type}.id = {res_type_id} AND code='{code}';
            """.format(fields=', '.join(fields),
                       code_type=code_type,
                       res_type=res_type,
                       res_type_id=res_type_id,
                       code=code
                       )
    # logger.debug(query)
    data = None
    try:
        with con:
            cur = con.cursor()
            cur.execute(query)
            data = cur.fetchone()
    except Exception as e:
        logger.error("Retrieval of code {code} ({code_type}) from "
                     "table {table} failed"
                     .format(code=code, code_type=code_type, table=res_type))
        logger.error(query)
        logger.error(e)

    if data:
        data = dict(zip(fields, data))

    return data

if __name__ == '__main__':
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

    rootlogger.debug(DATABASE)
    # Alessandro Manzoni
    # print query_pages('2719455')
    # print
    # print query_pages('14854')
    # print
