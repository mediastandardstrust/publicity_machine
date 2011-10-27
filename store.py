import pickle
import os
import errno
import logging

AUTOSAVE_THRESHOLD = 10

class Store:
    """
    Abstracts out an interface to churnalism server, and
    keeps track of which documents have been uploaded
    """

    def __init__(self,name):
        # file to track which ones have been added
        self.filename = name + ".store"
        self.cnt = 0

        try:
            f = open(self.filename,'r')
            self.index = pickle.load(f)
        except IOError as e:
            if e.errno!=errno.ENOENT:
                raise
            self.index = set()

    def save(self):
        if self.cnt==0:
            return

        tmp = self.filename + ".tmp"
        bak = self.filename + ".bak"

        f = open(tmp,'w')
        pickle.dump(self.index,f)
        if os.path.isfile(self.filename):
            os.rename(self.filename,bak)
        os.rename(tmp,self.filename)
        if os.path.isfile(bak):
            os.unlink(bak)

        self.cnt=0
        logging.debug("store saved")

    def already_got(self, url):
        return url in self.index


    # url
    # date (epoch)
    # title
    # company (source)
    # text

    # topics
    # location
    # language
    #
    def add(self,doc):
        url = doc['url']
        #doc_id = 

        # call _post()
        #http://us.churnalism.com/document/<doctype>/<id>/
        # check response

        # great - now update our local record of stored docs
        self.index.add(url)
        self.cnt += 1
        logging.info("stored %s",url)
        if self.cnt > AUTOSAVE_THRESHOLD:
            self.save()

    def _post(url, **kwargs):
        req = urllib2.Request(url)

        if kwargs:
            req.add_data(urllib.urlencode(kwargs))

        auth = 'Basic ' + base64.urlsafe_b64encode("%s:%s" % (USER, PASS))
        req.add_header('Authorization', auth)

        return urllib2.urlopen(req)

