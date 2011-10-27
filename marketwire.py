import lxml.html
import re
import urllib2
from pprint import pprint
import datetime
import util


# "EAST PEORIA, Ill., Oct. 24, 2011 /PRNewswire/ -- "...
dateline_pat = re.compile(r'(?P<location>.*?),\s*(?P<month>\w{3})[.]?\s*(?P<day>\d{1,2}),\s*(?P<year>\d{4})\s*/(?P<wire>.*?)/\s*--\s*',re.DOTALL)

def extract(html):
    doc = lxml.html.fromstring(html)

    main = doc.cssselect('#newsroom-copy')[0]

    content_div = main.cssselect('.mw_release')[0]
    title_div = main.cssselect('h1')[0]

    title = unicode(title_div.text_content())
    content = util.render_text(content_div)

    print title
    print "---------------"
    print content

    # break up dateline, eg
#    m = dateline_pat.search(content)
#    pprint(m.group('month'))


def main():
    test_url = "http://www.marketwire.com/press-release/unwind-this-autumn-with-a-wood-fired-oven-by-the-stone-bake-oven-company-1577177.htm"

    html = urllib2.urlopen(test_url).read()
    extract(html)

main()

