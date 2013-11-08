#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sqlite3 as sqlite
from subprocess import Popen, PIPE

# global
DATABASE = 'sbnredirect.db'

# logging
logger = logging.getLogger('sbnredirect.database')

# SELECT page_id, page_title, page_touched, page_latest, page_len FROM pagelinks, page 
# WHERE pl_title="Controllo_di_autorità" AND page_id=pl_from AND page_namespace=0 
# LIMIT 10;
# query = """ SELECT page_id, page_title, page_touched, page_latest, page_len
#         FROM pagelinks, page 
#         WHERE pl_title="Controllo_di_autorità" 
#             AND page_id=pl_from 
#             AND page_namespace=0 
#         """

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
                           viaf(code TEXT PRIMARY KEY,
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
                                 linked TEXT)
                        """)
            cur.execute("""CREATE TABLE 
                           Data(id BIGINT PRIMARY KEY,
                                title TEXT,
                                touched BIGINT, 
                                latest BIGINT,
                                linked TEXT)
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

def write_codes(code_name, code_value, page=None, data=None, linked=None):

    logger.debug('value: %s' %(code_value and (page or data)) )

    if code_value and (page or data):
        con = sqlite.connect(DATABASE)

        if page is None:
            page = {}

        if data is None:
            data = {}

        query = None
        if page.get('pageid', None):
          query = """INSERT OR REPLACE INTO
                         {code_name}(code,
                                     page_id,
                                     data_id
                                    )
                          VALUES("{code_value}", 
                                 {page_id},
                                 (SELECT data_id 
                                  FROM {code_name} 
                                  WHERE code = "{code_value}")
                               )
                  """.format(
                      code_name=code_name,
                      code_value=code_value,
                      page_id=page['pageid']
                     )

        if data.get('pageid', None):
          query = """INSERT OR REPLACE INTO
               {code_name}(code,
                           page_id,
                           data_id
                          )
                VALUES("{code_value}", 
                       (SELECT page_id 
                        FROM {code_name} 
                        WHERE code = "{code_value}"),
                       {data_id}
                     )
                """.format(
                    code_name=code_name,
                    code_value=code_value,
                    data_id=data['pageid']
                   )
        
        if query:  
          # logger.debug(query)
          try:
              with con:
                  cur = con.cursor()
                  cur.execute(query)
          except Exception as e:
              logger.error("Insertion of codes into table {code_name}"\
                           " failed".format(code_name=code_name))
              logger.error(query)
              logger.error(e)

          con = sqlite.connect(DATABASE)

          sources = {'Pages': page, 'Data': data}

          for s in sources:
              datum = sources[s]
              logger.debug('{s}: {datum}'.format(s=s, datum=datum))
              if datum:

                  query = """INSERT OR REPLACE INTO 
                                 {table}(id,
                                         title,
                                         touched,
                                         latest,
                                         linked
                                        )
                                 VALUES({id}, 
                                        "{title}",
                                        {touched},
                                        {latest},
                                        {linked}
                                       )
                              """.format(
                                  table=s,
                                  id=datum['pageid'] or 'NULL',
                                  title=datum['title'].encode('utf-8') or 'NULL',
                                  touched=datum['touched'] or 'NULL',
                                  latest=datum['lastrevid'] or 'NULL',
                                  linked=linked or 'NULL'
                                 )
                  try:
                      with con:
                          cur = con.cursor()

                          cur.execute(query)
                  except Exception as e:
                      logger.error("Insertion into {table} failed".format(
                          table=s))
                      logger.error(query)
                      logger.error(e)


FIELDS = ("id", "title", "touched", "latest")

def query(table, page_id):
    con = sqlite.connect(DATABASE)

    query = """SELECT id, title, touched, latest
               FROM {table}
               WHERE id = "{page_id}"
            """.format(table=table, page_id=page_id)

    # logger.debug(query)
    data = None
    try:
        with con:
            cur = con.cursor()
            cur.execute(query)
            data = cur.fetchone()
    except Exception as e:
        logger.error("Retrieval of code {page_id} from table {table} failed"\
                     .format(page_id=page_id))
        logger.error(query)
        logger.error(e)

    if data:
        data = dict(zip(FIELDS, data))

    return data

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


    # Alessandro Manzoni
    print query_pages('2719455')
    print
    print query_pages('14854')
    print