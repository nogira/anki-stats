# package version
__version__ = "0.1.1"


from os.path import exists, abspath
from requests import get
csv_path = abspath(__file__+'/../unigram_freq.csv')
if exists(csv_path):
    pass
else:
    with open(csv_path, 'w') as f:
        url = 'https://raw.githubusercontent.com/nogira/anki-stats/main/unigram_freq.csv'
        f.write(get(url).text)
        del url
del csv_path

from .db_class import *
