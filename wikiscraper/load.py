#!/usr/bin/python
# -*- coding: utf-8 -*-

import fileinput
from StringIO import StringIO
from lxml import etree
import urllib
import urllib2

SERVER_URL="http://127.0.0.1:8080/document/10/"

def post(id,url,title,text):
  print id,title,url
  req=urllib2.Request("%s%s/"%(SERVER_URL,id))
  data={"id":id,"url":url,"title":title.encode('utf-8'),"text":text.encode('utf-8')}
  req.add_data(urllib.urlencode(data))
  return urllib2.urlopen(req)

def process(xml):
  xml="<root>%s</root>"%xml
  parser=etree.XMLParser(recover=True)
  tree=etree.fromstring(xml,parser=parser)
  for doc in tree.xpath("//doc"):
    etree.strip_tags(doc,"a")
    title=doc.text.split("\n")[1]
    text="\n".join(doc.text.split("\n")[2:])
    url=doc.get("url").replace("http://it.wikipedia.org","http://en.wikipedia.org")
    post(doc.get("id"),url,title,text)

fi = fileinput.FileInput(openhook=fileinput.hook_compressed)
xml=StringIO()
for line in fi:
  xml.write(line)
process(xml.getvalue())

