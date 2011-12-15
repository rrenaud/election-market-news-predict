#!/usr/bin/python

import os

def main():
  existing_output_list = set(os.listdir('text_results/'))
  for fn in os.listdir('results/'):
      output_fn = 'text_results/' + fn
      if fn not in existing_output_list:
          print 'converting', fn
          os.system('w3m results/%s -T text/html > %s' % (fn, output_fn))
          
if __name__ == '__main__':
    main()
