#!/usr/bin/python

import simplejson as json
import os
import pprint
import urllib2
import sha

def main():
    existing_results = set(os.listdir('results/'))
    for fn in os.listdir('searches/'):
        try:
            contents = json.load(open('searches/' + fn))
            results = contents['bossresponse']['news']['results']
        except KeyError, e:
            print 'skipping', fn
            continue
        except json.decoder.JSONDecodeError, e:
            print 'skipping', fn
            continue
        date = fn[-8:]
        for result in results:
            url = result['url']
            out_fn = date + '.' + sha.sha(url).hexdigest()
            if out_fn in existing_results:
                print 'skipping', url
            else:
                print 'getting', url
                try:
                    open('results/' + out_fn, 'w').write(
                        urllib2.urlopen(url, timeout=20).read())
                    existing_results.add(out_fn)
                except Exception, e:
                    print 'skipping', url, 'because', e

if __name__ == '__main__':
    main()
