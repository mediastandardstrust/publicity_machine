import pickle
import os
import errno
import logging
import csv
import superfastmatch
from pprint import pprint
import base64

AUTOSAVE_THRESHOLD = 10


class StoreFailure(Exception):
    pass

class DummyStore:

    def __init__(self,name,doc_type):
        logging.info("running against dummy store")
        pass

    def save(self):
        pass

    def already_got(self, url):
        return False

    def add(self,doc):
        url = doc['url']
        for f in ('url','date','title','source','text'):
            if f not in doc:
                raise Exception("missing '%s' field" %(f))
        logging.info("store: %s (%s)",url,doc['title'])


class Store:
    """
    Abstracts out an interface to churnalism server, and
    keeps track of docids which have been uploaded
    """


    def __init__(self, name, doc_type, auth_user, auth_pass, server):

        self.USER = auth_user
        self.PASS = auth_pass
        self.SERVER = server

        self._sfm = superfastmatch.Client(url='http://' + server + '/', 
                                          parse_response=True,
                                          username=auth_user, 
                                          password=auth_pass)

        # file to track which ones have been added
        self.filename = name + ".docids"
        self.doc_type = doc_type

        self.cnt = 0    # count uncommited docs
        self.index = {}
        self.doc_id = 1

        try:
            f = open(self.filename,'r')
            reader = csv.reader(f)
            for row in reader:
                self.index[row[1]] = int(row[0])
            f.close()
            self.doc_id = max(self.index.values()) + 1

        except IOError as e:
            if e.errno!=errno.ENOENT:
                raise
            logging.warning("starting new store")
        logging.info("store ready: next doc_id is %d",self.doc_id)

    def save(self):
        if self.cnt==0:
            return

        tmp = self.filename + ".tmp"
        bak = self.filename + ".bak"

        f = open(tmp,'w')
        writer = csv.writer(f)
        for url,doc_id in self.index.iteritems():
            writer.writerow((doc_id,url))
        f.close()

        if os.path.isfile(self.filename):
            os.rename(self.filename,bak)
        os.rename(tmp,self.filename)
        if os.path.isfile(bak):
            os.unlink(bak)

        self.cnt=0
        logging.debug("store saved")

    def already_got(self, url):
        return url in self.index


    def add(self,doc):
        url = doc['url']

        for f in ('url','date','title','source','text'):
            if f not in doc:
                raise Exception("missing '%s' field" %(f))

        doc_id = self.doc_id

        try:
            self._sfm.add(doctype=self.doc_type, 
                          docid=doc_id, 
                          **doc)

            # great - now update our local record of stored docs
            self.index[url] = self.doc_id
            logging.info("store %d: %s",self.doc_id,url)
            self.doc_id += 1
            self.cnt += 1
            if self.cnt > AUTOSAVE_THRESHOLD:
                self.save()
        except superfastmatch.SuperFastMatchError, e:
            raise StoreFailure('Failed to store document: {0}'.format(str(e)))
        #return doc_id

