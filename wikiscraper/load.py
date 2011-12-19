#!/usr/bin/python
# -*- coding: utf-8 -*-

from StringIO import StringIO
from lxml import etree
import urllib3
import fnmatch
import os
import argparse
import bz2
from multiprocessing import Pool,Lock,Value

parser = argparse.ArgumentParser(description='Load wikipedia articles.')
parser.add_argument('dirname', action='store', help='Path to the parent folder containing bzip files')

conn = urllib3.HTTPConnectionPool("127.0.0.1:8080",maxsize=4)

def post(data):
  with lock:
    docid.value+=1
    url="/document/10/%s/"%docid.value
  response=conn.request_encode_body("POST",url,data,encode_multipart=False)
  print "POST: %s %s %s %s"%(response.status,url,data["id"],data["title"])

def processFile(filename):
  xml="<root>%s</root>"%bz2.BZ2File(filename, 'rb').read()
  parser=etree.XMLParser(recover=True)
  tree=etree.fromstring(xml,parser=parser)
  etree.strip_tags(tree,"a")
  for doc in tree.xpath("//doc"):
    text=doc.text.encode('utf-8').split("\n")
    post({
      'id'    : doc.get("id"),
      'title' : text[1],
      'text'  : "\n".join(text[2:]),
      'url'   : doc.get("url").replace("http://it.wikipedia.org","http://en.wikipedia.org")
    })

def getFiles(path):
  matches = []
  for root, dirnames, filenames in os.walk(path):
    for filename in fnmatch.filter(filenames, '*.bz2'):
      yield os.path.join(root,filename)

def main():
  pool = Pool(processes=4)
  pool.map(processFile,getFiles(parser.parse_args().dirname))

if __name__ == "__main__":
  docid = Value('I',1)
  lock = Lock()
  main()