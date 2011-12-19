#!/usr/bin/python
# -*- coding: utf-8 -*-

from StringIO import StringIO
from lxml import etree
import httplib
import urllib
import urllib2
import fnmatch
import os
import argparse
import bz2

parser = argparse.ArgumentParser(description='Load wikipedia articles.')
parser.add_argument('dirname', action='store', help='Path to the parent folder containing bzip files')

SERVER_URL="127.0.0.1:8080"
POST_HEADERS={"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}


def post(conn,doc_id,data):
  conn.request("POST","/document/10/%s/"%doc_id,urllib.urlencode(data),POST_HEADERS)
  response=conn.getresponse()
  response.read()
  print "POST: %s %s %s %s"%(response.status,doc_id,data["id"],data["title"])

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

def main():
  doc_id=1
  conn = httplib.HTTPConnection(SERVER_URL)
  for file in getFiles(parser.parse_args().dirname):
    for data in process(bz2.BZ2File(file, 'rb').read()):
      post(conn,doc_id,data)
      doc_id+=1

if __name__ == "__main__":
  main()