import lxml.html

def decode_string(s):
    encodings = ['ascii', 'windows-1252', 'latin1', 'utf-8']
    for (idx, enc) in enumerate(encodings, start=1):
        try:
            return (enc, s.decode(enc))
        except UnicodeDecodeError:
            if idx == len(encodings):
                raise
            else:
                pass

def render_text(el):
    """ like lxml.html text_content(), but with tactical use of whitespace for block elements """

    inline_tags = ( 'a', 'abbr', 'acronym', 'b', 'basefont', 'bdo', 'big',
        'br',
        'cite', 'code', 'dfn', 'em', 'font', 'i', 'img', 'input',
        'kbd', 'label', 'q', 's', 'samp', 'select', 'small', 'span',
        'strike', 'strong', 'sub', 'sup', 'textarea', 'tt', 'u', 'var',
        'applet', 'button', 'del', 'iframe', 'ins', 'map', 'object',
        'script' )

    txt = u''
    if isinstance(el, lxml.html.HtmlComment):
        return txt

    tag = str(el.tag).lower()
    if tag not in inline_tags:
        txt += u"\n";

    if el.text is not None:
        txt += unicode(el.text)
    for child in el.iterchildren():
        txt += render_text(child)
        if child.tail is not None:
            txt += unicode(child.tail)

    if el.tag=='br' or tag not in inline_tags:
        txt += u"\n";
    return txt

# from fuzzydate
month_names = {
    '01': 1, '1':1, 'jan': 1, 'january': 1,
    '02': 2, '2':2, 'feb': 2, 'february': 2,
    '03': 3, '3':3, 'mar': 3, 'march': 3,
    '04': 4, '4':4, 'apr': 4, 'april': 4,
    '05': 5, '5':5, 'may': 5, 'may': 5,
    '06': 6, '6':6, 'jun': 6, 'june': 6,
    '07': 7, '7':7, 'jul': 7, 'july': 7,
    '08': 8, '8':8, 'aug': 8, 'august': 8,
    '09': 9, '9':9, 'sep': 9, 'september': 9, 'sept': 9,
    '10': 10, '10':10, 'oct': 10, 'october': 10,
    '11': 11, '11':11, 'nov': 11, 'november': 11,
    '12': 12, '12':12, 'dec': 12, 'december': 12,
    # es
    'enero': 1,
    'febrero': 2,
    'marzo': 3,
    'abril': 4,
    'mayo': 5,
    'junio': 6,
    'julio': 7,
    'agosto': 8,
    'septiembre': 9,
    'octubre': 10,
    'noviembre': 11,
    'diciembre': 12,
}

def lookup_month(name):
    """ resolve month name to month number 1-12"""
    return month_names[name.lower()]


def dump(pr):
    """ dump a press release summary to stdout """
    enc = 'utf-8'
    N = 150

    print('-'*10)
    for f in pr:
        val = pr[f]
        if not isinstance(val,unicode):
            val = unicode(pr[f])
        val = val.encode(enc)
        if len(val.split('\n')) > 1:
            print "###%s###\n%s" %(f,val)
        else:
            print "###%s###: %s" %(f,val)

