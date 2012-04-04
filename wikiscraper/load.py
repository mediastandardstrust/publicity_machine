#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division

import fnmatch
import os
import math
import datetime
import argparse
import superfastmatch
from pprint import pprint
from lxml import etree

TODAY = datetime.date.today()

parser = argparse.ArgumentParser(description='Load wikipedia articles.')
parser.add_argument('--verbose', '-v', action='count', help='Print confirmation for each document submitted to the SuperFastMatch server.')
parser.add_argument('--mindoclen', action='store', type=int, default=360, metavar='LEN', help='The minimum character length of a document in order to be included, defaults to 360 characters or approximately 4 sentences.')
parser.add_argument('dirname', action='store', help='Path to the parent folder containing bzip files')
parser.add_argument('host', action='store', help='Hostname of the SuperFastMatch server.')
parser.add_argument('port', action='store', help='Port of the SuperFastMatch server.')
parser.add_argument('doctype', action='store', help='Doctype to use for loaded documents.')
args = parser.parse_args()

def bifurcate(func, iterable):
    ts = []
    fs = []
    for item in iterable:
        if func(item):
            ts.append(item)
        else:
            fs.append(item)
    return (ts, fs)

def add_document(data, docid):
  sfm = superfastmatch.Client(url='http://{host}:{port}'.format(host=args.host, 
                                                                port=args.port), 
                              parse_response=True)
  result = sfm.add(args.doctype, docid, defer=True, **data)
  if result['success'] == True:
    if args.verbose:
      print "{0}, {1}: '{2}'".format(args.doctype, docid, data['title'])
  else:
      print "Failed to add '{0}'".format(data['title'])

def processFile(first_docid, filename):
  with file(filename, 'rb') as xmlfile:
    xml = "<root>%s</root>" % xmlfile.read()
  parser=etree.XMLParser(recover=True)
  tree=etree.fromstring(xml,parser=parser)
  etree.strip_tags(tree,"a")
  def inclusion_filter(doc):
    return (not doc.get('url', '').endswith(u'_(disambiguation)') 
            and not u'List_of_' in doc.get('url', '')
            and len(doc.text.strip()) >= args.mindoclen)
  (kept, dropped) = bifurcate(inclusion_filter, tree.xpath('//doc'))
  print "Dropped %s of %s documents" % (len(dropped), len(kept) + len(dropped))
  docs = list(enumerate(kept, start=first_docid))
  for (docid, doc) in docs:
    text=doc.text.encode('utf-8').split("\n")
    attrs = {
      'id'    : doc.get("id"),
      'title' : text[1],
      'text'  : "\n".join(text[2:]),
      'source': 'Wikipedia',
      'date'  : TODAY,
      'url'   : doc.get("url", "").replace("http://it.wikipedia.org","http://en.wikipedia.org")
    }
    add_document(attrs, docid)
  print "Processed %s docs from %s" % (len(docs), filename)
  return docs[-1][0]

def getFiles(path):
  for root, dirnames, filenames in os.walk(path):
    for filename in fnmatch.filter(filenames, 'wiki*'):
      yield os.path.join(root,filename)

def main():
  previous_docid = 1
  files = list(getFiles(args.dirname))
  files.sort()
  for (filenum, filename) in enumerate(files, start=1):
    print "Processing %s (%s of %s)" % (filename, filenum, len(files))
    previous_docid = processFile(previous_docid + 1, filename)
  print "Processed all files, waiting for workers to terminate."

if __name__ == "__main__":
  main()
