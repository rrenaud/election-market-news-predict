#!/usr/bin/python

import collections
import datetime
import os
import random
import subprocess
import time

import numpy
import scikits.learn.svm

import cand_sentences
import date_util
import intrade_data_parser
import vw_learner

class FeatureIndexer:
    def __init__(self):
        self.feature_mapping = {}
        self.reverse_mapping = []

    def feature_index(self, feature):
        if feature not in self.feature_mapping:
            self.feature_mapping[feature] = len(self.feature_mapping)
            self.reverse_mapping.append(feature)
        return self.feature_mapping[feature]

    def num_features(self):
        return len(self.feature_mapping)

    def get_ith_feature_name(self, i):
        return self.reverse_mapping[i]

def tokenize_contents(contents):
    for line in contents:
        split_line = map(str.lower, line.split())
        for token in split_line:
            yield token.replace(',', '').replace('.', '').replace(':', '')

def tokenize(fn):
    for tok in tokenize_contents(open(fn)):
        yield tok

class DocumentReader:
    def get_doc_contents(self, candidate, date):
        return open(cand_sentences.SENTENCES_DIR + candidate + '.' + date)

class BagOfWordsDocumentEncoder:
    def __init__(self, stopwords, feature_indexer, doc_reader):
        self.stopwords = stopwords
        self.feature_indexer = feature_indexer
        self.doc_reader = doc_reader

    def encode_doc(self, candidate, date):
        contents = self.doc_reader.get_doc_contents(candidate, date)
        return self.encode_contents(contents)
        #return numpy.clip(ret, 0.0, 1.0)

    def encode_contents(self, contents, vec = None):
        if vec is None:
            vec = numpy.zeros(self.feature_indexer.num_features())

        for token in tokenize_contents(contents):
            if token not in self.stopwords:
                vec[self.feature_indexer.feature_index(token)] += 1
            
        return vec

class TrendingEncoder:
    def __init__(self, subencoder, hist_size, smoothing):
        self.subencoder = subencoder
        self.hist_size = hist_size
        self.smoothing = smoothing

    def encode_doc(self, candidate, date):
        cur = date
        this_raw_doc = self.subencoder.encode_doc(candidate, date)
        overall = numpy.zeros(len(this_raw_doc.copy()))
        for i in range(self.hist_size):
            cur = date_util.prev_day(cur)
            prev_raw_doc = self.subencoder.encode_doc(candidate, date)
            overall += prev_raw_doc
        overall += self.smoothing
        return this_raw_doc / (self.hist_size * overall)

class FakeLearner:
    def __init__(self):
        self.name = 'fake'

    def predict(self, candidate, date):
        return random.choice([-1, 1])

    def fit(self, candidate_date_list, labels_list):
        pass

    def real(self): return False

class BasePredictor:
    def __init__(self, encoder):
        self.encoder = encoder

    def predict(self, candidate, date):
        return self.predict_vec(self.encoder.encode_doc(candidate, date))

    def predict_contents(self, contents, vec=None):
        return self.predict_vec(self.encoder.encode_contents(contents, vec))

class SvmPredictor:
    def __init__(self, encoder, name):
        BasePredictor.__init__(self, encoder)
        self.learner = scikits.learn.svm.LinearSVC()
        self.name = name

    def predict_vec(self, vec):
        return self.learner.predict(vec)[0]
    
    def fit(self, candidate_date_list, labels_list):
        vectors = []
        for candidate, date in candidate_date_list:
            vectors.append(self.encoder.encode_doc(candidate, date))
        numpy_vectors = numpy.array(vectors)
        numpy_labels = numpy.array(labels_list)
        self.learner.fit(numpy_vectors, numpy_labels)

    def real(self): return True

class VorpalCandPricePredictor(BasePredictor):
    def __init__(self, encoder, name):
        BasePredictor.__init__(self, encoder)
        self.vw_learner = vw_learner.VwLearner()
        self.name = name

    def predict_vec(self, vec):
        return self.vw_learner.predict(self._vec_to_vw(vec))
 
    def fit(self, candidate_date_list, labels_list):
        for (candidate, date), label in zip(candidate_date_list, labels_list):
            numpy_vec = self.encoder.encode_doc(candidate, date)
            self.vw_learner.learn(self._vec_to_vw(numpy_vec), label)

    def real(self): return True

    def _vec_to_vw(self, vec):
        vw_vec = []
        if hasattr(vec, 'iteritems'):
            iteritems = vec.iteritems()
        else:
            iteritems = enumerate(vec)
        for ind, val in iteritems:
            if val != 0:
                vw_vec.append('%d:%f' % (ind, val))
        return vw_vec
            
def avg(l):
    return float(sum(l)) / len(l)

class EvaluationStats:
    def __init__(self, learner, doc_reader):
        self.acc = []
        self.profit_list = []
        self.learner = learner
        self.doc_reader = doc_reader
        
    def eval_prediction(self, actual, cand, date):
        prediction = self.learner.predict(cand, date)
        decision = 1 - 2 * (prediction < 0)
        if decision * actual > 0:
            self.acc.append(1)
        elif decision * actual == 0:
            self.acc.append(.5)
        else:
            self.acc.append(0)
        self.profit_list.append(decision * actual)

        if self.learner.real():
            doc_contents = self.doc_reader.get_doc_contents(cand, date)
            sentences = [l for l in doc_contents]
            output_fn = 'debug_output/%s.%s.%s.html' % (
                cand, date, self.learner.name)
            print 'writing debug output', output_fn
            scored_sentences = []
            for sentence in sentences:
                prediction = self.learner.predict_contents(
                    [sentence], collections.defaultdict(float))
                scored_sentences.append((prediction, sentence))

            scored_sentences.sort()
            output_file = open(output_fn, 'w')
            output_file.write('<html>')
            output_file.write('<meta http-equiv="Content-Type" '
                              'content="text/html;charset=utf-8" />')
            output_file.write('<head><title>%s %s %s</title></head>' %
                              (cand, date, self.learner.name))
            output_file.write('<body>')
            output_file.write('prediction: %.4f<br>' % prediction)
            output_file.write('actual: %.4f<br>' % actual)
            output_file.write('<table>')
            for score, sentence in scored_sentences:
                output_file.write('<tr><td>%.4f</td><td>%s</td></tr>' %
                                  (score * 100, sentence))
            output_file.write('</table>')
            output_file.write('</body>')
            output_file.write('</html>')
            output_file.close()
            
    def accuracy(self):
        return avg(self.acc)

    def profit(self):
        return sum(self.profit_list)

def precompute_feature_indexer_size(feature_indexer, grouped_sentence_files):
    # Just get the overall number of features in all of the training data,
    # this information is not used to predict, only to make correctly
    # sized feature vectors.
    for date in sorted(grouped_sentence_files):
        for file_name in grouped_sentence_files[date]:
            for token in tokenize(cand_sentences.SENTENCES_DIR + file_name):
                feature_indexer.feature_index(token)

def main():
    intrade_parser = intrade_data_parser.IntradeDataParser()
    feature_indexer = FeatureIndexer()
    
    print 'reading sentences'
    grouped_sentence_files = cand_sentences.grouped_sentence_files_by_date()
    #for k, v in grouped_sentence_files.iteritems():
        #grouped_sentence_files[k] = [x for x in v if 'gingrich' in x]
    #while len(grouped_sentence_files) > 10:
    #    grouped_sentence_files.popitem()

    print 'precomputing feature sizes'
    precompute_feature_indexer_size(feature_indexer, grouped_sentence_files)

    doc_reader = DocumentReader()
    stopwords = set(map(str.strip, open('english.stop').readlines()))
    stopworded_encoder = BagOfWordsDocumentEncoder(stopwords, feature_indexer,
                                                   doc_reader)
    plain_encoder = BagOfWordsDocumentEncoder(set(), feature_indexer,
                                              doc_reader)
    stopworded_trend_encoder3_10 = TrendingEncoder(stopworded_encoder, 3, 10)
    plain_trend_encoder3_10 = TrendingEncoder(plain_encoder, 3, 10)
    learners = [#SvmPredictor(stopworded_encoder, 'stopword_svm'), 
                #SvmPredictor(plain_encoder, 'plain_svm'),
                #SvmPredictor(stopworded_trend_encoder3_10, 'stop_trend_3_10'),
                #SvmPredictor(plain_trend_encoder3_10, 'plain_trend_3_10')
        VorpalCandPricePredictor(stopworded_encoder, 'stop_vow_all')
        ]
    for i in range(100):
        fake_learner = FakeLearner()
        learners.append(fake_learner)
    eval_stats = [EvaluationStats(learner, doc_reader) for learner in learners]

    training_data = []
    labels = []
    dates_to_skip = 5

    for date in sorted(grouped_sentence_files):
        if date[-1] == '2' or date[-1] == '7':
            continue
        #if dates_to_skip <= -5: break
        print date
        for file_name in grouped_sentence_files[date]:
            cand = file_name[:file_name.find('.'):]
            cur, next = intrade_parser.get_cur_and_next_price(cand, date)
            change = next - cur
            training_data.append((cand, date))
            labels.append(change)
            if dates_to_skip > 0:
                continue

            for learner, eval_stat in zip(learners, eval_stats):
                eval_stat.eval_prediction(change, cand, date)

        dates_to_skip -= 1
        if dates_to_skip <= 0:
            for learner in learners:
                learner.fit(training_data, labels)

    coefs = []
    print 'num features', feature_indexer.num_features()
    # print 'coef size', len(learners[0].learner.coef_[0])
    # for ind in range(feature_indexer.num_features()):
    #     coefs.append((feature_indexer.get_ith_feature_name(ind), 
    #                   learners[0].learner.coef_[0][ind]))
    # coefs.sort(key = lambda x: -abs(x[1]))
    # for feature, weight in coefs[:500]:
    #     print feature, weight
    
    eval_stats.sort(key=lambda x: -x.profit())
    for ind, e in enumerate(eval_stats):
        if e.learner.name != 'fake':
            print e.learner.name, 'profit', ind, float(ind) / len(eval_stats), e.profit()
    eval_stats.sort(key=lambda x: -x.accuracy())
    for ind, e in enumerate(eval_stats):
        if e.learner.name != 'fake':
            print e.learner.name, 'accuracy', ind, float(ind) / len(eval_stats), e.accuracy()

if __name__ == '__main__':
    main()
