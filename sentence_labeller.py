
import collections
import os
import sha
import urlparse

import cand_sentences

LABELLED_SENTENCES_DIR = 'labelled_sentences/'

def sentence_hash(sentence):
    if not isinstance(sentence, str):
        sentence = sentence.replace(u'\u2019', "'").replace('\u201d', '"')
        sentence = sentence.encode('ascii', 'ignore')
    return sha.sha(sentence.strip()).hexdigest()

def hash_sentences_for_day(date):
    hashed_sentences = {}
    sentence_files = cand_sentences.grouped_sentence_files_by_date()[date]    
    for sentence_file in sentence_files:
        for sentence in open(
            cand_sentences.SENTENCES_DIR + '/' + sentence_file):
            hashed_sentences[sentence_hash(sentence)] = sentence
    return hashed_sentences

def hash_ratings(parsed_query):
    ratings_by_hash = collections.defaultdict(list)
    for key in parsed_query:
        if '-' in key:  # heuristic to detect ratings rather than other 
            # query  parameters
            cand, sentence_hash = key.split('-')
            val = parsed_query[key][0]
            ratings_by_hash[sentence_hash].append((cand, val))
    return ratings_by_hash

def serialize_ratings_with_sentence(ratings, sentence):
    return (';'.join([cand + ',' + val for cand, val in ratings]) + 
            ':' + sentence)

def write_joined_records(hashed_ratings, hashed_sentences, date):
    ret = ''
    successes = 0
    fails = 0
    for hash_val in hashed_ratings:
        if hash_val in hashed_sentences:
            successes += 1
            serialized = serialize_ratings_with_sentence(
                hashed_ratings[hash_val], hashed_sentences[hash_val])
            open(LABELLED_SENTENCES_DIR + date + '.' + hash_val, 'w').write(
                serialized)
        else:
            ret += 'warning, ignoring ' + hash_val + '\n'
            fails += 1
    ret += 'successes: %d\n' % successes
    ret += 'failures: %d\n' % fails
    return ret

def record_data(data):
    parsed_query = urlparse.parse_qs(data)
    date = parsed_query['date'][0]

    hashed_ratings = hash_ratings(parsed_query)
    hashed_sentences = hash_sentences_for_day(date)

    return write_joined_records(hashed_ratings, hashed_sentences, date)

class LabelledSentenceReader:
    def __init__(self):
        self.file_list = set(os.listdir(LABELLED_SENTENCES_DIR))

    def get_labels(self, date, sentence):
        ret = collections.defaultdict(str)
        filename = date + '.' + sentence_hash(sentence)
        if filename not in self.file_list:
            return ret
        contents = open(LABELLED_SENTENCES_DIR + filename).read()
        ratings = contents.split(':')[0]
        cand_rating_pair_strings = ratings.split(';')
        for cand_rating_pair_string in cand_rating_pair_strings:
            cand, rating = cand_rating_pair_string.split(',')
            ret[cand] = rating
        return ret
