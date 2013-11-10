#! /usr/bin/env python\
# -*- coding: utf-8 -*-

import pywikibot
import logging
import wikipedia_template_parser as wtp

# logging
logger = logging.getLogger('sbnredirect.item')

# globals
CODES = {
'viaf': None,
'lccn': None,
'sbn': None
}

INFO = {
'pageid': None,
'title': None,
'touched': None,
'lastrevid': None
}

# create a site object for it.wiki
SITE = pywikibot.getSite('it', 'wikipedia')
REPO = SITE.data_repository()

# utility functions
def normalize_string(string):
    return string.lower().replace(' ', '_').encode('utf-8')

class Item(object):

    class Entity(object):

        def __init__(self, ent_type, name):
            self.type = ent_type
            self.name = name
            self.codes = None

        def __repr__(self):
            return u'Item.{type}(name={name})'.format(
                type=self.type,
                name=repr(self.name))

        @property
        def title(self):
            return self.name

    class Page(Entity):

        def __init__(self, name, info):
            super(type(self), self).__init__(
                  ent_type='page',
                  name=name and name.replace(' ', '_'),
                 )
            self.WikiPage = None
            self.set_WikiPage()
            self.info = None
            self.set_info(info)

        @property
        def id(self):
            pageid = (isinstance(self.WikiPage, pywikibot.Page) and \
                        self.WikiPage._pageid)
            if pageid:
                return pageid

        def set_WikiPage(self):
            if not self.WikiPage:
                if self.name:
                    try:
                         self.WikiPage = pywikibot.Page(SITE, self.name)
                         self.page = self.WikiPage.get()
                    except Exception as e:
                         logger.error(e)

            return self.WikiPage

        def get_codes(self):

            if self.codes:
                return self.codes

            self.codes = CODES.copy()

            templates = []
            try:
                if self.name:
                    templates = wtp.data_from_templates(self.name, lang='it')
            except Exception as e:
                logger.error(e)

            ac_template = [t for t in templates
                           if normalize_string(t['name']) == \
                                'controllo_di_autorità']
            ac_data = ac_template[0]['data'] if ac_template else {}

            # logger.debug('ac_data: {data}'.format(data=ac_data))

            if ac_data.get('VIAF') is not None:
                self.codes['viaf'] = ac_data['VIAF'].encode('utf-8')

            if ac_data.get('SBN') is not None:
                self.codes['sbn'] = ac_data['SBN'].encode('utf-8')

            if ac_data.get('LCCN') is not None:
                self.codes['lccn'] = ac_data['LCCN'].encode('utf-8')

            return self.codes

        def __touched(self):
            touched = isinstance(self.WikiPage, pywikibot.Page) and \
                        str(self.WikiPage.editTime())
            if touched:
                return touched.replace('-','').replace(':','').\
                            replace('T','').replace('Z','')

        def __lastrevid(self):
            lastrevid = isinstance(self.WikiPage, pywikibot.Page) and \
                            self.WikiPage.latestRevision()
            if lastrevid:
               return lastrevid

        def set_info(self, info=None):
            if info is not None:
                self.info = INFO.copy()
                self.info['pageid'] = info['pageid']
                self.info['title'] = info['title']
                self.info['touched'] = info['touched'].replace('-','').\
                                       replace(':','').replace('T','').\
                                       replace('Z','')
                self.info['lastrevid'] = info['lastrevid']
            else:
                if not self.info or not self.info['pageid']:
                    self.info = INFO.copy()
                    self.info['pageid'] = self.id
                    self.info['title'] = self.title
                    self.info['touched'] = self.__touched()
                    self.info['lastrevid'] = self.__lastrevid()

            if self.info == INFO:
                self.info = None

    class Data(Entity):

        def __init__(self, name, info):
            super(type(self), self).__init__(
                  ent_type='data',
                  name=name,
                 )
            self.ItemPage = None
            self.set_ItemPage()
            self.info = None
            self.set_info(info)

        @property
        def id(self):
            pageid = (isinstance(self.ItemPage, pywikibot.ItemPage) and \
                      self.ItemPage.id)
            if pageid:
                return pageid

        def set_ItemPage(self):
            if not self.ItemPage:
                if self.name:
                    try:
                        self.ItemPage = pywikibot.ItemPage(REPO, self.name)
                        self.data = self.ItemPage.get()
                    except Exception as e:
                        logger.error(e)
            
            return self.ItemPage

        def __get_page_id_from_API(self):
            if isinstance(self.ItemPage, pywikibot.ItemPage):
                page = self.ItemPage.toggleTalkPage().toggleTalkPage()
                page.get()
                return page._pageid

        def __get_page_id_from_DB(self):
            raise ValueError

        def __page_id(self):

            page_id = None
            try:
                page_id = self.__get_page_id_from_DB()
            except ValueError as e:
                # logger.error(e)
                pass
            
            if not page_id:
                page_id = self.__get_page_id_from_API()

            if page_id:
                return page_id

        def __touched(self):
            touched = isinstance(self.ItemPage, pywikibot.ItemPage) and \
                        str(self.ItemPage.editTime())
            if touched:
                return touched.replace('-','').replace(':','').\
                            replace('T','').replace('Z','')

        def __lastrevid(self):
            lastrevid = isinstance(self.ItemPage, pywikibot.ItemPage) and \
                            self.ItemPage.latestRevision()
            if lastrevid:
                return lastrevid

        def set_info(self, info=None):
            if info is not None:
                self.info = INFO.copy()
                self.info['pageid'] = info['pageid']
                self.info['title'] = info['title']
                self.info['touched'] = info['touched'].replace('-','').\
                                       replace(':','').replace('T','').\
                                       replace('Z','')
                self.info['lastrevid'] = info['lastrevid']
            else:
                if not self.info or not self.info['pageid']:
                    self.info = INFO.copy()
                    
                    self.info['pageid'] = self.__page_id()
                    self.info['title'] = self.title
                    self.info['touched'] = self.__touched()
                    self.info['lastrevid'] = self.__lastrevid()

            if self.info == INFO:
                self.info = None

        def get_codes(self):

            if self.codes:
                return self.codes

            self.codes = CODES.copy()

            if isinstance(self.ItemPage, pywikibot.ItemPage):

                # VIAF identifier is Property:P214
                if 'P214' in self.ItemPage.claims:  
                    self.codes['viaf'] = self.ItemPage.claims['P214'][0].\
                                            getTarget()

                # SBN identifier is Property:P396
                if 'P396' in self.ItemPage.claims:
                    self.codes['sbn'] = self.ItemPage.claims['P396'][0].\
                                            getTarget()

                #LCCN identifier is Property:P244
                if 'P244' in self.ItemPage.claims:
                    self.codes['lccn'] = self.ItemPage.claims['P244'][0].\
                                            getTarget()

            return self.codes

    def __init__(self, page=None, data=None, info=None):
        if page or data:
            self.page = self.Page(page, info=(page and info) or None)
            self.data = self.Data(data, info=(data and info) or None)
            self.set_page_name()
            self.set_data_name()
        else:
            raise ValueError('Either page or data should be provided')

    def __repr__(self):
        return u'Item(page={page}, data={data})'.format(
            page=repr(self.page), 
            data=repr(self.data))

    def set_page_name(self):
        if not self.page.name:
            try:
                self.page.name = self.data.data['sitelinks']['itwiki']
            except Exception as e:
                logger.error(e)

            if self.page.name:
                self.page.set_WikiPage()
                self.page.set_info()

    def set_data_name(self):
        if not self.data.name:        
            try:
                self.data.ItemPage = pywikibot.ItemPage.\
                                        fromPage(self.page.WikiPage)
                self.data.data = self.data.ItemPage.get()
                self.data.name = self.data.ItemPage.id
            except Exception as e:
                logger.error(e)

            if self.data.name:
                self.data.set_info()

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
    rootlogger.setLevel(logging.INFO)

    lvl_config_logger = logging.DEBUG

    console = logging.StreamHandler()
    console.setLevel(lvl_config_logger)

    formatter = logging.Formatter(LOGFORMAT_STDOUT[lvl_config_logger])
    console.setFormatter(formatter)

    rootlogger.addHandler(console)

    item = Item(page='Alessandro Manzoni')
    print item.page.get_codes()
    print item.data.get_codes()

    item2 = Item(data='Q1064')
    print item2.data.get_codes()
    print item2.page.get_codes()

    import pdb
    pdb.set_trace()