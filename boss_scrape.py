#!/usr/bin/python

import datetime
import httplib2
import os
import urllib
import time

import oauth2

import candidate_info

OAUTH_CONSUMER_KEY = open('consumer_key.txt', 'r').read().strip()
OAUTH_CONSUMER_SECRET = open('consumer_secret.txt', 'r').read().strip()

url_fmt = (
    "http://yboss.yahooapis.com/ysearch/news?"
    "q=%(query)s&age=%(age)dd-%(age2)dd&start=%(start)d")

def make_request(query, days_ago, start):
    then_date = datetime.datetime.now() - datetime.timedelta(days_ago)
    date_format = then_date.strftime('%Y%m%d')
    output_fn = 'searches/' + query.replace(' ', '_') 
    if start > 0:
        output_fn += '.start=' + str(start)
    output_fn += '.' + date_format
    if os.path.exists(output_fn):
        print output_fn, 'exists for', query, date_format
        return

    consumer = oauth2.Consumer(key=OAUTH_CONSUMER_KEY,
                               secret=OAUTH_CONSUMER_SECRET)
    params = {
        'oauth_version': '1.0',
        'oauth_nonce': oauth2.generate_nonce(),
        'oauth_timestamp': int(time.time()),
    }

    url = url_fmt % {'query': urllib.quote('"' + query + '"'), 
                     'age': days_ago,  'age2': days_ago + 1,
                     'start': start}
    print url
    oauth_request = oauth2.Request(method='GET', url=url, parameters=params)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), 
                               consumer, None)
    oauth_header=oauth_request.to_header(realm='yahooapis.com')
    
    http = httplib2.Http()
    resp, content = http.request(url, 'GET', headers=oauth_header)
    print url
    time.sleep(1)
    open(output_fn, 'w').write(content)

if __name__ == "__main__":
    for i in range(1, 30):
        for start in range(0, 1000, 50):
            for cand in candidate_info.candidates:
                # this could be a lot smarter, paying attention to the
                # total number of results to avoid making spurious requests.
                make_request(cand, i, start)
