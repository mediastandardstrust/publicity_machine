#!/usr/bin/env python

import lxml.html
import requests
from dateutil.parser import parse
from churn.basescraper import BaseScraper
from util import readability_extract

class ACGAScraper(BaseScraper):
    name = 'acga'
    doc_type = 7
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.102011-10-16 20:23:50'
    }

    def find_latest(self):
        url = 'http://www.acga.org/index.php?option=com_content&task=blogsection&id=1&Itemid=42'
        req = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.102011-10-16 20:23:50'})
        if req.status_code != 200:
            return []
        
        doc = lxml.html.fromstring(req.content)
        links = [a.attrib['href'] for a in doc.cssselect('a.contentpagetitle')]
        return links

    def extract(self, html, link):
        (title, body) = readability_extract(html)

        document = lxml.html.fromstring(html.encode('utf-8'))
        date_cells = document.cssselect('td.createdate')
        date = date_cells[0].text_content().strip() if len(date_cells) == 1 else None
        doc = {
            'url': link,
            'title': title,
            'text': body,
            'date': parse(date),
            'source': 'ACGA News & Views'
        }
        return doc

if __name__ == '__main__':
    scraper = ACGAScraper()
    scraper.main()
