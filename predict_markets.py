#!/usr/bin/python

import collections
import datetime
import os
import time

import mlpy
import numpy
import scikits.learn.svm

import cand_sentences
import intrade_data_parser

class FeatureIndexer:
    def __init__(self):
        self.feature_mapping = {}

    def feature_index(self, feature):
        if feature not in self.feature_mapping:
            self.feature_mapping[feature] = len(self.feature_mapping)
        return self.feature_mapping[feature]

    def num_features(self):
        return len(self.feature_mapping)

def tokenize(fn):
    for line in open(fn):
        split_line = map(str.lower, line.split())
        for token in split_line:
            yield token

def encode_document_as_word_feature_counts(fn, feature_indexer):
    ret = numpy.zeros(feature_indexer.num_features())
    for token in tokenize(fn):
        ret[feature_indexer.feature_index(token)] += 1
    return ret

def main():
    intrade_parser = intrade_data_parser.IntradeDataParser()
    feature_indexer = FeatureIndexer()
    sentence_files = os.listdir('sentences/')
    def extract_date(fn):
        return fn[-8:]
    sentence_files.sort(key=extract_date)
    grouped_files = collections.defaultdict(list)

    for file_name in sentence_files:
        grouped_files[extract_date(file_name)].append(file_name)
        for token in tokenize('sentences/' + file_name):
            feature_indexer.feature_index(token)

    # learner = mlpy.Svm()
    learner = scikits.learn.svm.LinearSVC()
    acc = 0.0
    tries = 0

    training_data = []
    labels = []
    dates_to_skip = 5
    for date in sorted(grouped_files):
        if date[-1] == '0' or date[-1] == '5':
            continue
        for file_name in grouped_files[date]:
            cand = file_name[:file_name.find('.'):]
            change = intrade_parser.get_price_change(cand, date)
            feature_vec = encode_document_as_word_feature_counts(
                'sentences/' + file_name, feature_indexer)
            training_data.append(feature_vec)
            labels.append(2 * int(change > 0) - 1)
            print change, cand, date
            if dates_to_skip > 0:
                continue

            # prediction = learner.predict(feature_vec)
            prediction = learner.predict(feature_vec)
            if prediction * change > 0:
                acc += 1
                print 'correct'
            elif prediction * change == 0:
                acc += .5
                print 'tie'
            else:
                print 'incorrect'
            tries += 1
            print date, cand, prediction, change, acc, tries

        dates_to_skip -= 1
        if dates_to_skip <= 0:
            start = time.time()
            #learner.compute(numpy.array(training_data), numpy.array(labels))
            learner.fit(numpy.array(training_data), numpy.array(labels))
            print time.time() - start

if __name__ == '__main__':
    main()
