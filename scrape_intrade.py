#!/usr/bin/python

import urllib

INTRADE_PREFIX = 'https://www.intrade.com/graphing/jsp/downloadClosingPrice.jsp?contractId='

CAND_TO_INTRADE_ID = {'gingrich': 654836,
                      'romney': 652757,
                      'huntsman': 658927,
                      'paul': 669534,
                      'perry': 656777,
                      'bachman': 745285,
                      'cain': 745220}

for cand, intrade_id in CAND_TO_INTRADE_ID.iteritems():
    url = INTRADE_PREFIX + str(intrade_id)
    contents = urllib.urlopen(url).read()
    open('intrade_data/' + cand + '.csv', 'w').write(contents)
                      
