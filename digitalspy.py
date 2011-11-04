#!/usr/bin/python
# -*- coding: utf-8 -*-

from lxml.html import parse,tostring,fromstring
from lxml.html.clean import clean_html
from lxml.etree import strip_elements,strip_tags
import urllib2,urllib
import re

BREAKS = re.compile(r'<br */? *>\s*<br */? *>')
ARTICLES = re.compile(r'.*/a(\d+)/.*')

def getLinks(page):
  url="http://www.digitalspy.co.uk/headlines/?page=%s"%page
  try:
    html=urllib2.urlopen(url).read()
  except IOError:
    print "Skipping: %s"% url
    return []
  links=[]
  for headline in fromstring(html).cssselect('table.headlines-container')[1].cssselect("div.article_title_text a"):
    match=ARTICLES.match(headline.get("href"))
    if match:
      links.append(match.group(1))
  return links

def getPage(id):
  url="http://www.digitalspy.co.uk/news/a%s"%id
  try:
    html=urllib2.urlopen(url).read()
  except IOError:
    print "Skipping: %s"% url
    return None
  html=clean_html(html)
  html=BREAKS.sub("\n",html)
  doc=fromstring(html)
  article=doc.cssselect("div.article_body")[0]
  for image in article.xpath('//div[@class="image"]|//div[@class="imgcaption"]'):
    image.getparent().remove(image)
  strip_elements(article,'img')
  return {
    'url'       : url,
    'title'     : doc.cssselect("div.article_header h1")[0].text_content().encode('utf-8'),
    'published' : doc.cssselect("span.time")[0].text_content().encode('utf-8'),
    'authors'   : ",".join(editor.text_content().encode('utf-8') for editor in doc.cssselect("span.editors a")),
    'text'      : article.text_content().strip().encode('utf-8')
  }

def postPage(doc_id,data):
  post_url = "http://127.0.0.1:8080/document/11/%s/" % (doc_id)
  req = urllib2.Request(post_url)
  req.add_data(urllib.urlencode(data))
  try:
    urllib2.urlopen(req)
    print "Posted: %s with id: %s"%(data["url"],doc_id)
    return True
  except urllib2.URLError:
    print "Problem with: %s"%data["url"]
    return False
    

# for id in [344689,344636,338928,342139,341018,340526,336742,329570,327839,326479,283435,154580,333508,340372]:
doc_id=1;
for page in xrange(1,5500):
  for id in getLinks(page):
    data=getPage(id)
    if data and postPage(doc_id,data):
      doc_id+=1
      


