import re

CONDENSE_WHITESPACE = re.compile('[^\S\n]+', re.UNICODE)
CONDENSE_NEWLINES = re.compile('\s*\n+\s*', re.UNICODE)


def condense_whitespace(string):
    
    #condense all whitespace (except newlines) to a single space
    string = re.sub(CONDENSE_WHITESPACE, ' ', string)

    #combine multiple newlines into one
    string = re.sub(CONDENSE_NEWLINES, '\n', string)

    return string

