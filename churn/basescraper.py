import logging
import urllib2
from optparse import OptionParser
import ConfigParser

from urllib2helpers import CacheHandler
from store import Store,DummyStore



# TODO: add option to run as a daemon...
class BaseScraper(object):
    """ basic scraper framework for grabbing press releases

    Derived scrapers generally need to implement:
    name          - string name of the scraper
    doc_type      - numeric document type for uploaded press releases
    find_latest() - to grab a list of the latest press releases (usually
                    from an rss feed)
    extract()     - parse html data to pull out the various text and metadata
                    of the press release
    """
    def __init__(self):

        # derived classes need to set these
        assert self.name is not None
        assert self.doc_type is not None

        self.parser = OptionParser(usage="%prog: [options]")
        self.parser.add_option('-v', '--verbose', action='store_true')
        self.parser.add_option('-d', '--debug', action='store_true')
        self.parser.add_option('-t', '--test', action='store_true', help="test only - don't send any documents to server")
        self.parser.add_option('-c', '--cache', action='store_true', help="cache all http transfers in .cache dir (for repeated runs during test)")
        self.parser.add_option('-u', '--url', nargs=1, help="process just the given URL")
        self.parser.add_option('-i', '--ini-file', default="churnalism.cfg", nargs=1, help="filename for connection settings [default: %default]")


    def main(self):
        """ set everything up, then invoke go() """

        (options, args) = self.parser.parse_args()

        log_level = logging.ERROR
        if options.debug:
            log_level = logging.DEBUG
        elif options.verbose:
            log_level = logging.INFO
        logging.basicConfig(level=log_level)    #, format='%(message)s')


        if options.test:
            self.store = DummyStore(self.name, self.doc_type)
        else:
            # load in config file for real run
            config = ConfigParser.ConfigParser()
            config.readfp(open(options.ini_file))
            auth_user = config.get("DEFAULT",'user')
            auth_pass = config.get("DEFAULT",'pass')
            server = config.get("DEFAULT",'server')

            self.store = Store(self.name, self.doc_type, auth_user=auth_user, auth_pass=auth_pass, server=server)


        if options.cache:
            logging.info("using .cache")
            opener = urllib2.build_opener(CacheHandler(".cache"))
            urllib2.install_opener(opener)

        self.go(options)


    def go(self,options):
        """ perform the actual scraping

        default implementation is to just call find_latest and process the discovered press releases.
        But it's likely derived classes will want to handle custom options for fetching historical
        data

        see prnewswire for an example.
        """


        if options.url:
            urls = [options.url,]
        else:
            urls = self.find_latest()

        self.process_batch(urls)


    def process_batch(self, urls):
        """ run through a list of urls, fetching, extracting and storing each in turn """

        # cull out ones we've got
        n_before = len(urls)
        urls = [url for url in urls if not self.store.already_got(url)]
        logging.info("processing %d urls (%d are new)", n_before, len(urls))

        err_cnt = 0
        try:

            for url in urls:
                try:
                    logging.debug("fetch %s",url)
                    response = urllib2.urlopen(url)
                    html = response.read()
                    # TODO: maybe just skip ones which redirect to other domains?
                    if response.geturl() != url:
                        logging.warning("Redirect detected %s => %s",url,response.geturl())
                    press_release = self.extract(html, url)

                    # encode text fields
                    # TODO: use isinstance(...,unicode) instead
                    for f in ('url','title','source','text','location','language','topics'):
                        if f in press_release:
                            press_release[f] = press_release[f].encode('utf-8')
                    self.store.add(press_release)

                except Exception as e:
                    logging.error("failed on %s: %s %s",url,e.__class__,e)
                    err_cnt += 1
        finally:
            self.store.save()


    def find_latest(self):
        """ obtain the list of "latest" press releases, whatever that means for a given target """
        return []


    def extract(self,html,url):
        """ extract a single downloaded press release """
        assert False    # need to implement in derived class!



