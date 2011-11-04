wget http://download.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2
mkdir extracted
bzip2 -dc enwiki-latest-pages-articles.xml.bz2 |./WikiExtractor.py -cb 10M -o extracted
./load.py extracted