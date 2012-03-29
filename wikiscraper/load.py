#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division

import fnmatch
import os
import math
import argparse
import superfastmatch
from pprint import pprint
from lxml import etree
from multiprocessing import Pool, cpu_count

parser = argparse.ArgumentParser(description='Load wikipedia articles.')
parser.add_argument('--verbose', '-v', action='count', help='Print confirmation for each document submitted to the SuperFastMatch server.')
parser.add_argument('dirname', action='store', help='Path to the parent folder containing bzip files')
parser.add_argument('host', action='store', help='Hostname of the SuperFastMatch server.')
parser.add_argument('port', action='store', help='Port of the SuperFastMatch server.')
parser.add_argument('doctype', action='store', help='Doctype to use for loaded documents.')
args = parser.parse_args()

def add_document(data, docid):
  sfm = superfastmatch.Client(url='http://{host}:{port}'.format(host=args.host, 
                                                                port=args.port), 
                              parse_response=True)
  sfm.add(args.doctype, docid, **data)
  if args.verbose:
    print "{0}, {1}: '{2}'".format(args.doctype, docid, data['title'])

def create_pool():
  processes = 2
  try:
    processes = int(math.ceil(cpu_count() * 2))
  except NotImplementedError:
    pass
  return Pool(processes=processes)

def processFile(first_docid, filename):
  pool = create_pool()
  with file(filename, 'rb') as xmlfile:
    xml = "<root>%s</root>" % xmlfile.read()
  parser=etree.XMLParser(recover=True)
  tree=etree.fromstring(xml,parser=parser)
  etree.strip_tags(tree,"a")
  docgen = (doc for doc in tree.xpath("//doc") 
            if not doc.get('url', '').endswith(u'_(disambiguation)')
            and not doc.get('url', '').startswith(u'List_of'))
  docs = list(enumerate(docgen, start=first_docid))
  for (docid, doc) in docs:
    text=doc.text.encode('utf-8').split("\n")
    attrs = {
      'id'    : doc.get("id"),
      'title' : text[1],
      'text'  : "\n".join(text[2:]),
      'url'   : doc.get("url", "").replace("http://it.wikipedia.org","http://en.wikipedia.org")
    }
    pool.apply_async(add_document, [attrs, docid])
  pool.close()
  pool.join()
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
