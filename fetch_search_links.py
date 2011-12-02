#!/usr/bin/python

import simplejson as json
import os
import pprint
import urllib
import sha

def main():
    for fn in os.listdir('searches/'):
        contents = json.load(open('searches/' + fn))
        try:
            results = contents['bossresponse']['news']['results']
        except KeyError, e:
            print 'skipping', fn
            continue
        date = fn[-8:]
        for result in results:
            url = result['url']
            out_fn = 'results/' + date + '.' + sha.sha(url).hexdigest()
            if os.path.exists(out_fn):
                print 'skipping', url
            else:
                print 'getting', url
                open(out_fn, 'w').write(urllib.urlopen(url).read())

if __name__ == '__main__':
    main()
