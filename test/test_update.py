#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging

basedir = os.path.realpath('..')
if basedir not in sys.path:
    sys.path.append(basedir)

import update as up

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

if __name__ == '__main__':
    CONFIG_FILENAME = 'update.cfg'
    config_file = os.path.realpath(os.path.join('..', CONFIG_FILENAME))

    rootlogger.debug(config_file)
    up.read_config(config_file)
