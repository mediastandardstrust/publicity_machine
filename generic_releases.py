#!/usr/bin/env python

import logging
import re
from optparse import OptionParser
from readability.readability import Document 
import urllib2 as  ulib
from lxml import etree, html
from churn import util, fuzzydate
from churn.basescraper import BaseScraper
from dateutil.parser import parse
from dateutil.tz import * 
from datetime import *

#this is a list of urls we want to get scrapable links from
from job_list import rss_feed_no_body
from util import condense_whitespace

class GenericRSSScraper(BaseScraper):
    name = "generic_rss_scraper"
    doc_type = 5
    extra = {}

    def __init__(self):
        super(GenericRSSScraper, self).__init__()
    

    def go(self, options):
        readable_links = []
        dates = []
        names = []

        for article in rss_feed_no_body:
            
            name = article['name']
            url = article['feed_url']
            feed = etree.parse(ulib.urlopen(url))
            for item in feed.iter('item'):
                for link in item.iter('link'):
                    readable_links.append(link.text)
                for date in item.iter('pubDate'):
                    dates.append(date.text.replace('Sept.', 'Sep'))

                names.append(name)
    
        self.extra = { 'source': names, 
                  'links': readable_links, 
                  'dates': dates  }

        self.process_batch(readable_links)
#        self.extract(readable_links)  #process_batch

    def extract(self, response, link): #extract

#    for link in link_list:
    #       response = ulib.urlopen(link).read()
            
        #get relevant content using readability
        readable = Document(response)
        body = readable.summary()
        title = readable.short_title()

        #strip extra html readability leaves in, like p tags
        title = html.fromstring(title).text_content()
        body = html.fromstring(body).text_content()
        title = condense_whitespace(title)
        body = condense_whitespace(body)

        links = self.extra['links']
       
        try: 
            d = unicode(self.extra['dates'][links.index(link)])
        except:
            #pr web rss feeds don't have pubdate
            html_body = html.fromstring(response)
            d = re.sub('.*\(.*\)', '', html_body.find_class('releaseDateline')[0].text_content())

        #print d
                        

        date = parse(d)

        doc = { 'url': link,
                'title': title,
                'text': body,
                'date': date,
                'source': self.extra['source'][links.index(link)]}

        return doc

if __name__ == '__main__':
    scraper = GenericRSSScraper()
    scraper.main()

