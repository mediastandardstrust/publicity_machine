#!/usr/bin/env python

import re
import logging
from optparse import OptionParser
from readability.readability import Document 
import urllib2 as  ulib
from lxml import etree, html
from churn import util, fuzzydate
from churn.basescraper import BaseScraper
from dateutil.parser import parse
from dateutil.tz import * 
from datetime import *

from util import condense_whitespace

class CongressLeadership(BaseScraper):
    urls = ['http://www.speaker.gov/News/DocumentQuery.aspx?DocumentTypeID=689',
            'http://majorityleader.gov/Newsroom/',
            'http://www.democraticleader.gov/news/facts',
            'http://www.democraticwhip.gov/newsroom/whips-report',
            'http://www.majoritywhip.gov/blog',
            'http://www.reid.senate.gov/newsroom/press_releases.cfm',
            'http://mcconnell.senate.gov/public/index.cfm?p=PressReleases' ]

    leaders = ['speaker', 'house_majority_leader',]
    sources = ['Speaker of the House Press Releases', 'House Majority Leader Press Releases', ]
    name = "congressional_leadership_scraper"
    doc_type = 6
    links = []
    extra = {}

    def __init__(self, index):
        self.index =  index
        super(CongressLeadership, self).__init__()

    def parse_house_majority_leader_date(self, date_text, response):
        date_obj = html.fromstring(response)
        date = parse(date_obj.find_class('published')[0].get('title'))
        return date


    def parse_speaker_date(self, date_text, response):
        text = html.fromstring(date_text).xpath('//b')
        date = datetime.today()

        for t in text:
            matches = re.findall('((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)+(\s*\d+)(,\s*\d{4})*)', t.text_content())
            if matches:
                date = parse(matches[0][0])

        return date

    def get_house_majority_links(self, leader):

        page = html.fromstring(ulib.urlopen(self.urls[self.index]).read())
        page.make_links_absolute(self.urls[0])
        link_list = page.get_element_by_id('recent_news_2').get_element_by_id('news_text').iterlinks()
        page_count = 1

        for l in link_list: #this corresponds to archive pages
            print "Parent page: %s" % l[2]
            page = html.fromstring(ulib.urlopen(l[2]).read())
            page.make_links_absolute(l[2])
            page_links = []
            page_link_containers = page.find_class('pioneer_inner_3')
            for p in page_link_containers: page_links.append(p.findall('a'))

            print len(page_links)
            for item in page_links:
                href = item[0].get('href')     
                if href not in self.links:
                    self.links.append(href)
                    print "got %s from page %s" % (href, page_count)

            page_count += 1 

        #need different helper functions for each member of leadership
        self.extra['leader'] = leader         


    def get_speaker_links(self, leader):

        page = html.fromstring(ulib.urlopen(self.urls[self.index]).read())
        page.make_links_absolute(self.urls[0])
        link_list = page.find_class('middlelinks')
        page_count = 1

        while link_list: # and page_count < 3:
            for item in link_list:
                link = item.get('href')
                
                if link not in self.links:
                    self.links.append(link)
                    print "got %s from page %s" % (link, page_count)

            page_count += 1 
            page = html.fromstring(ulib.urlopen(self.urls[0] + '&Page=%s' % page_count).read())

            page.make_links_absolute(self.urls[0])
            link_list = page.find_class('middlelinks')
            
            #need different helper functions for each member of leadership
            self.extra['leader'] = leader         


    def extract(self, response, link):

        readable = Document(response)
        body = readable.summary()
        title = readable.short_title()
        #try to get date for boehner's press releases

        #how to find out where speaker links start?
        date = getattr(self, 'parse_%s_date'% self.extra['leader'])(body, response) 

        print date
        #strip extra html readability leaves in, like p tags
        title = html.fromstring(title).text_content()
        body = html.fromstring(body).text_content()
        title = condense_whitespace(title)
        body = condense_whitespace(body)
#        links = extra['links']
        

        doc = { 'url': link,
                'title': title,
                'text': body,
                'date': date,
                'source': self.sources[self.index]}

        return doc


    
    def go(self, options):
        if self.index == 0:
            self.get_speaker_links(self.leaders[self.index])
        elif self.index == 1:
            self.get_house_majority_links(self.leaders[self.index])
        print self.links
        self.process_batch(self.links)


if __name__ == '__main__':
#   scraper = CongressLeadership(0)
    scraper = CongressLeadership(1)
    scraper.main()


