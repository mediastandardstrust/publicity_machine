#!/usr/bin/env python

import re
import logging
import time
import httplib
from optparse import OptionParser
from readability.readability import Document 
from lxml import etree, html
from churn.basescraper import BaseScraper
from dateutil.parser import parse
from dateutil.tz import * 
from datetime import datetime
import requests
import feedparser

from util import readability_extract

class CongressLeadership(BaseScraper):
    urls = ['http://www.speaker.gov/News/DocumentQuery.aspx?DocumentTypeID=689',
            'http://majorityleader.gov/Newsroom/',
            'http://www.democraticleader.gov/news/press',
            'http://www.democraticwhip.gov/newsroom/press-releases',
            'http://www.majoritywhip.gov/newsroom',
            "http://www.reid.senate.gov/newsroom/press_releases.cfm?xml=Senator%20Reid's%20Press%20Releases,RSS2.0full",
            'http://mcconnell.senate.gov/public/index.cfm?p=PressReleases',
            'http://www.whitehouse.gov/briefing-room/statements-and-releases' ]

    leaders = ['speaker', 'house_majority_leader', 'house_minority_leader', 'house_minority_whip', 'house_majority_whip', 'senate_majority_leader', 'senate_minority_leader', 'white_house']
    sources = ['Speaker of the House Press Releases', 'House Majority Leader Press Releases', 'House Minority Leader Press Releases', 'House Minority Whip Press Releases', 'House Majority Whip Press Releases', 'Senate Majority Leader Press Releases', 'Senate Minority Leader Press Releases', 'White House Press Releases' ]
    name = "congressional_leadership_scraper"
    doc_type = 6
    links = []
    extra = {}

    def __init__(self, index):
        self.index =  index
        super(CongressLeadership, self).__init__()

    def parse_house_majority_leader_date(self, date_text, response, link):
        date_obj = html.fromstring(response)
        date = parse(date_obj.find_class('published')[0].get('title'))
        return date

    def parse_house_minority_leader_date(self, date_text, response, link):
        return parse(self.dates[self.links.index(link)])

    def parse_house_minority_whip_date(self, date_text, response, link):
        return parse(self.dates[self.links.index(link)])

    def parse_senate_majority_leader_date(self, date_text, response, link):
        return parse(self.dates[self.links.index(link)])

    def parse_senate_minority_leader_date(self, date_text, response, link):
        return parse(self.dates[self.links.index(link)])

    def parse_house_majority_whip_date(self, date_text, response, link):
        return parse(self.dates[self.links.index(link)])

    def parse_white_house_date(self, date_text, response, link):
        return parse(self.dates[self.links.index(link)])

    def parse_speaker_date(self, date_text, response, link):
        text = html.fromstring(date_text).xpath('//b')
        date = datetime.today()

        for t in text:
            matches = re.findall('((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)+(\s*\d+)(,\s*\d{4})*)', t.text_content())
            if matches:
                date = parse(matches[0][0])

        return date
    



    def get_speaker_links(self, leader):

        response = requests.get(self.urls[self.index])
        if response.status_code != httplib.OK:
            logging.error('{status}:{url}'.format(status=response.status_code, 
                                                  url=self.urls[self.index]))
            return

        page = html.fromstring(response.content)
        page.make_links_absolute(self.urls[0])
        link_list = page.find_class('middlelinks')
        page_count = 1
        self.links = []

        while link_list and page_count < 3: #don't want to scrape every page every day
            for item in link_list:
                link = item.get('href')
                
                if link not in self.links:
                    self.links.append(link)

            page_count += 1 
            response = requests.get(self.urls[0] + '&Page=%s' % page_count)
            if response.status_code == httplib.OK:
                page = html.fromstring(response.content)

                page.make_links_absolute(self.urls[0])
                link_list = page.find_class('middlelinks')
                
                #need different helper functions for each member of leadership
                self.extra['leader'] = leader         

    def get_house_majority_leader_links(self, leader):

        response = requests.get(self.urls[self.index])
        if response.status_code != httplib.OK:
            logging.error('{status}:{url}'.format(status=response.status_code, 
                                                  url=self.urls[self.index]))
            return

        page = html.fromstring(response.content)
        page.make_links_absolute(self.urls[1])
        link_list = page.get_element_by_id('recent_news_2').get_element_by_id('news_text').iterlinks()
        page_count = 1

        self.links = []

        for l in link_list: #this corresponds to archive pages

            if page_count > 2: break #don't want to get every page every time

            response = requests.get(l[2])
            if response.status_code == httplib.OK:
                page = html.fromstring(response.content)
                page.make_links_absolute(l[1])
                page_links = []
                page_link_containers = page.find_class('pioneer_inner_3')
                for p in page_link_containers: page_links.append(p.findall('a'))

                for item in page_links:
                    href = item[0].get('href')     
                    if href not in self.links:
                        self.links.append(href)
        
            page_count += 1 

        #need different helper functions for each member of leadership
        self.extra['leader'] = leader         

    def get_house_minority_leader_links(self, leader):
        response = requests.get(self.urls[self.index])
        if response.status_code != httplib.OK:
            logging.error('{status}:{url}'.format(status=response.status_code, 
                                                  url=self.urls[self.index]))
            return

        page = html.fromstring(response.content)
        page.make_links_absolute(self.urls[2].replace('/news/press', ''))
        self.dates = []
        self.links = []
        for item in page.find_class('teaser'):
            self.links.append(item.find('h3').find('a').get('href'))
            self.dates.append(item.find_class('date')[0].find('a').text_content())

        self.extra['leader'] = leader

    def get_house_minority_whip_links(self, leader):
        #forbidden to bots...
        headers = {
                    "Host":"www.democraticwhip.gov",
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
        response = requests.get(self.urls[self.index], headers=headers)
        if response.status_code == httplib.OK:
            page = html.fromstring(response.content)
            page.make_links_absolute(self.urls[3].replace('/newsroom/press-releases', ''))
            linklist = page.find_class('views-row')
            self.dates = []
            self.links = []
            for item in linklist:
                self.links.append(item.find('.//a').get('href'))
                self.dates.append(item.find_class('date-display-single')[0].text_content())
                time.sleep(2)
            self.extra['leader'] = leader

    def get_house_majority_whip_links(self, leader):
        response = requests.get(self.urls[self.index])
        if response.status_code != httplib.OK:
            logging.error('{status}:{url}'.format(status=response.status_code, 
                                                  url=self.urls[self.index]))
            return

        page = html.fromstring(response.content)
        page.make_links_absolute(self.urls[4].replace('/newsroom', ''))
        self.dates = []
        self.links = []
        for item in page.find_class('list-item'):
            self.links.append(item.find('h4').find('a').get('href'))
            self.dates.append(item.find_class('date')[0].text_content())

        self.extra['leader'] = leader

    def get_senate_majority_leader_links(self, leader):
        
        feed = feedparser.parse(self.urls[5])
        self.links = [e.link for e in feed.entries]
        self.dates = [e.date for e in feed.entries]
        self.extra['leader'] = leader

    def get_senate_minority_leader_links(self, leader):

        response = requests.get(self.urls[self.index])
        if response.status_code != httplib.OK:
            logging.error('{status}:{url}'.format(status=response.status_code, 
                                                  url=self.urls[self.index]))
            return

        page = html.fromstring(response.content)
        page.make_links_absolute(self.urls[6].replace('/public/index.cfm?p=PressReleases', ''))
        link_list = page.find_class('recordListTitle')
        dates = page.find_class('recordListDate')
        count = 0
        self.links = []
        self.dates = []
        for l in link_list:
            self.links.append(l.find('a').get('href'))
            self.dates.append(dates[count].text_content().replace('-', ''))
            count += 1

        self.extra['leader'] = leader

    def get_white_house_links(self, leader):
        response = requests.get(self.urls[self.index])
        if response.status_code != httplib.OK:
            logging.error('{status}:{url}'.format(status=response.status_code, 
                                                  url=self.urls[self.index]))
            return

        page = html.fromstring(response.content)
        page.make_links_absolute(self.urls[7].replace('/briefing-room/statements-and-releases',''))
        link_list = page.find_class('views-row')
        self.dates = []
        self.links = []
        for item in link_list:
            self.links.append(item.find('.//a').get('href'))
            self.dates.append(item.find_class('date-line')[0].text_content())
        
        self.extra['leader'] = leader


    def extract(self, response, link):

        (title, body) = readability_extract(response)

        #how to find out where speaker links start?
        date = getattr(self, 'parse_%s_date'% self.extra['leader'])(body, response, link) 

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
            self.get_house_majority_leader_links(self.leaders[self.index])
        elif self.index == 2:
            self.get_house_minority_leader_links(self.leaders[self.index])
        elif self.index == 3:
            self.get_house_minority_whip_links(self.leaders[self.index])
        elif self.index == 4:
            self.get_house_majority_whip_links(self.leaders[self.index])
        elif self.index == 5:
            self.get_senate_majority_leader_links(self.leaders[self.index])
        elif self.index == 6:
            self.get_senate_minority_leader_links(self.leaders[self.index])
        elif self.index == 7:
            self.get_white_house_links(self.leaders[self.index])

        self.process_batch(self.links)


if __name__ == '__main__':
#    scraper = CongressLeadership(7)
#    scraper.main()
    for index in [0,1,2,3,4,5,6,7]:
        scraper = CongressLeadership(index)
        scraper.main()


