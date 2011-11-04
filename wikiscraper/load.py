#!/usr/bin/python
# -*- coding: utf-8 -*-

from StringIO import StringIO
from lxml import etree
import urllib
import urllib2
import fnmatch
import os
import argparse
import bz2

parser = argparse.ArgumentParser(description='Load wikipedia articles.')
parser.add_argument('dirname', action='store', help='Path to the parent folder containing bzip files')

SERVER_URL="http://127.0.0.1:8080/document/10/"

def post(doc_id,data):
  print "Posting: %s %s %s"%(doc_id,data["id"],data["title"])
  req=urllib2.Request("%s%s/"%(SERVER_URL,doc_id))
  req.add_data(urllib.urlencode(data))
  return urllib2.urlopen(req)

def process(xml):
  xml="<root>%s</root>"%xml
  parser=etree.XMLParser(recover=True)
  tree=etree.fromstring(xml,parser=parser)
  etree.strip_tags(tree,"a")
  for doc in tree.xpath("//doc"):
    text=doc.text.encode('utf-8').split("\n")
    yield {
      'id'    : doc.get("id"),
      'title' : text[1],
      'text'  : "\n".join(text[2:]),
      'url'   : doc.get("url").replace("http://it.wikipedia.org","http://en.wikipedia.org")
    }

def getFiles(path):
  matches = []
  for root, dirnames, filenames in os.walk(path):
    for filename in fnmatch.filter(filenames, '*.bz2'):
      matches.append(os.path.join(root, filename))
  return matches

doc_id=1
for file in getFiles(parser.parse_args().dirname):
  for data in process(bz2.BZ2File(file, 'rb').read()):
    post(doc_id,data)
    doc_id+=1

