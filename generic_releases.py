#!/usr/bin/env python

import logging
import re
import httplib
from datetime import *

import requests

from readability.readability import Document 
from lxml import etree, html
from dateutil.parser import parse
from dateutil.tz import * 
from churn.basescraper import BaseScraper
from util import condense_whitespace

#this is a list of urls we want to get scrapable links from
from job_list import rss_feed_no_body

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
            headers = {
                    "User-Agent":"Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.23) Gecko/20110921 Ubuntu/10.04 (lucid) Firefox/3.6.23",
                    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language":"en-us,en;q=0.5",
                    "Accept-Encoding":"gzip,deflate",
                    "Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                    "Keep-Alive": '115',
                    "Connection":"keep-alive",
                    "Cookie": "SESSe44492e3eff92ed36c02b54ede745fd0=f8u762lhlmo02lf6s9f1q58s83; has_js=1",
                    "If-Modified-Since":"Mon, 05 Mar 2012 21:05:37 GMT",
                    "If-None-Match": "80b1e5f8cd8bc5180b65f43da511070c",
                    "Cache-Control":"max-age=0",
                    "Content-Type":"text/html; charset=utf-8"
            }
            response = requests.get(url, headers=headers)
            if response.status_code != httplib.OK:
                continue
            try:
                feed = etree.fromstring(response.content)
            except:
                print name
                print url
                print response.content
                print "Could not parse xml!"
                continue 

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
        
        try:                
            date = parse(d)
        except:
            date = datetime.now()

        doc = { 'url': link,
                'title': title,
                'text': body,
                'date': date,
                'source': self.extra['source'][links.index(link)]}

        return doc

if __name__ == '__main__':
    scraper = GenericRSSScraper()
    scraper.main()

