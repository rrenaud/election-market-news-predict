#!/usr/bin/python

# This reads the intrade_data/ csv files.

import collections
import csv
import datetime
import os

import date_util

INTRADE_DIR = 'intrade_data/'

class IntradeDataParser:
    def __init__(self):
        self.candidate_price_lists = collections.defaultdict(
            lambda: collections.defaultdict(float))
                                                                 
        for fn in os.listdir(INTRADE_DIR):
            self._parse_intrade_file(INTRADE_DIR + fn)

    def _parse_intrade_file(self, fn):
        candidate = fn.split('/')[1].split('.')[0]
        for row in csv.DictReader(open(fn)):
            date = datetime.datetime.strptime(row['Date'], '%b %d, %Y')
            str_date = date.strftime('%Y%m%d')
            self.candidate_price_lists[candidate][str_date] = float(
                row['Close'])
            
    def candidate_closing_time_series(self, cand):
        return self.candidate_price_lists[cand]

    def get_cur_and_next_price(self, cand, date):
        candidate_series = self.candidate_closing_time_series(cand)
        next = date_util.day_difference(date, 1)
        return candidate_series[date], candidate_series[next]

if __name__ == '__main__':
    intrade_parser = IntradeDataParser()
    print intrade_parser.get_cur_and_prev_price('paul', '20111030')
