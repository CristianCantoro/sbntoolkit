#! /usr/bin/env python
# -*- coding: utf-8 -*-

def retrieve_page(lang, code):
	if lang == 'data' or lang == 'wikidata':
		page = 'Q1'
	else:
		page = 'Alessandro_Manzoni'
	return page