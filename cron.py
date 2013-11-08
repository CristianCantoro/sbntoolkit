#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import argparse

from item import Item, INFO
import database
import update

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

logger = logging.getLogger('sbnredirect.cron')

def get_items_with_info(items):
    items_to_process = []

    for item in items:

        if item['source']== 'data':
            # Wikidata item
            item = Item(data=item['title'], 
                        info=dict((k,item[k]) for k in INFO)
                       )

        else:
            # Wikipedia page
            item = Item(page=item['title'], 
                        info=dict((k,item[k]) for k in INFO)
                       )

        items_to_process.append(item)

    return items_to_process

def get_items_from_cli(items):

    items_to_process = []

    for itemname in items:

        if itemname.startswith('data:') or itemname.startswith('wikidata:'):
            # Wikidata item
            itemname = itemname.replace('wiki','').replace('data:','')
            item = Item(data=itemname)

        else:
            # Wikipedia page
            item = Item(page=itemname)

        items_to_process.append(item)

    return items_to_process

def save_authority_codes(items):

    count = 0
    total = len(items)
    for item in items:
        count += 1
        logger.debug("{count}/{total}".format(
                        count=count,
                        total=total
                        )
                    )
        logger.debug("processing {}".format(item))

        wikidata_codes = item.data.get_codes()
        wikipedia_codes = item.page.get_codes()

        for code in wikipedia_codes:
            database.write_codes(code, wikipedia_codes[code], page=item.page.info)

        for code in wikidata_codes:
            database.write_codes(code, wikidata_codes[code], data=item.data.info)

if __name__ == '__main__':

    logger.setLevel(logging.ERROR)

    parser = argparse.ArgumentParser(
        description='Update authority control codes from italian Wikipedia.')
    parser.add_argument('items', metavar='item', type=str, nargs='*',
                        help='Wikipedia pages or Wikidata items to update')
    parser.add_argument('--debug', action='store_true',
                       help='Set debug mode')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress all output except for CRITICAL errors')
    parser.add_argument('--verbose', '-v', action='count',
                       help='Verbosity level, can be -v or -vv')
    parser.add_argument('--drop', action='store_true',
                       help='Drop database and exit')
    parser.add_argument('--create', action='store_true',
                       help='Attemp to create database')
    parser.add_argument('--update', action='store_true',
                       help='Get all pages')
    parser.add_argument('--update-file', '-f', dest='upfile', action='store',
                       help='Get all pages')

    args = parser.parse_args()
    # print args

    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.INFO)
        if args.verbose == 1:
            logger.setLevel(logging.WARNING) 
    if args.quiet:
        logger.setLevel(logging.CRITICAL)

    if args.drop:
        database.drop()

    if args.create:
        database.create()

    if not args.drop:
        items_to_process = []
        if args.update:
            items_to_update = update.read_items_to_update(args.upfile)
            # logger.debug(items_to_update)
            items_to_process = get_items_with_info(items_to_update)
        else:
            items_to_process = get_items_from_cli(args.items)

        save_authority_codes(items=items_to_process)

    logger.debug("Done! Quit")