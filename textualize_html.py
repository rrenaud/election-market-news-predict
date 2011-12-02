#!/usr/bin/python

from BeautifulSoup import BeautifulSoup

import os

# http://stackoverflow.com/questions/3593784/html-to-text-conversion-using-python-language
def gettextonly(soup):
    v = soup.string
    if v == None:
        c = soup.contents
        resulttext=''
        for t in c:
            subtext = gettextonly(t)
            resulttext += subtext + ' '
        return resulttext
    else:
        return v.strip()    

def main():
  existing_output_list = set(os.listdir('text_results/'))
  for fn in os.listdir('results/'):
      output_fn = 'text_results/' + fn
      if fn not in existing_output_list:
          print 'converting', fn
          os.system('w3m results/%s -T text/html > %s' % (fn, output_fn))
          
if __name__ == '__main__':
    main()
