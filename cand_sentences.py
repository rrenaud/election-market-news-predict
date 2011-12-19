#!/usr/bin/python

# Extract sentences containing candidate names from the text articles for
# a given day.

import os
import collections
import nltk
import re

import candidate_info

TEXT_RESULTS_DIR = 'text_results/'
SENTENCES_DIR = 'mult_sentences/'

PUNCT_CHARS_RE = re.compile("[,\\.']")
# The ugly escaped characters are bullets that w3m likes to use for lists.
HEURISTIC_SPLITS = re.compile('\n{2}|[ ]{3}|\xe2\x80\xa2')

def normalize_token(token):
    split = re.sub(PUNCT_CHARS_RE, ' ', token.lower()).split()
    if len(split) > 0:
        return split[0]
    return ''

def clean_sentence(sentence): 
    return ' '.join(sentence.split()).strip()

def hack_sentencize(contents, sent_tokenizer):
    # like the nltk sentence splitter, but also split at double 
    # newlines and bullets, which w3m likes to leave around.
    for supposed_sentence in sent_tokenizer.tokenize(contents, sent_tokenizer):
        heuristic_splits = re.split(HEURISTIC_SPLITS, supposed_sentence)
        for sentence in heuristic_splits:
            if len(sentence) > 50 and len(sentence) < 500:
                yield sentence

def mentioned_cands(sentence):
    seen_cands = set()
    tokens = sentence.split()
    for token in tokens:
        norm_token = normalize_token(token)
        if norm_token in candidate_info.candidate_last_names:
            seen_cands.add(norm_token)
    return seen_cands

def extract_cand_sentences(contents, sent_tokenizer):
    ret = collections.defaultdict(set)
    for sentence in hack_sentencize(contents, sent_tokenizer):
        for cand in mentioned_cands(sentence):
            ret[cand].add(clean_sentence(sentence))
    return ret

def extract_cand_sentences_in_files(files, sent_tokenizer):
    ret = collections.defaultdict(set)
    for fn in files:
        per_article_sentences = extract_cand_sentences(
            open(TEXT_RESULTS_DIR + fn).read(), sent_tokenizer)
        for cand in per_article_sentences:
            ret[cand].update(per_article_sentences[cand])
    return ret

def text_results_files_by_date():
    """ Return a dictionary of lists of filenames, keys are dates """
    files_to_process = os.listdir(TEXT_RESULTS_DIR)
    files_by_date = collections.defaultdict(list)
    for fn in files_to_process:
        files_by_date[fn[:8]].append(fn)
    return files_by_date


def grouped_sentence_files_by_date():
    """ Return a dictionary of lists of filenames, keys are dates """
    sentence_files = os.listdir(SENTENCES_DIR)
    grouped_files = collections.defaultdict(set)
    def extract_date(fn):
        return fn[-8:]
    for file_name in sentence_files:
        grouped_files[extract_date(file_name)].add(file_name)
    return grouped_files

def main():
    files_by_date = text_results_files_by_date()
    existing_sentences = grouped_sentence_files_by_date()
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    for date in sorted(files_by_date):
        if date in existing_sentences:
            print 'skipping', date
            continue
        sentences_per_cand = extract_cand_sentences_in_files(
            files_by_date[date], sent_tokenizer)
        for cand in sentences_per_cand:
            output_file_name = SENTENCES_DIR + cand + '.' + date
            output_file = open(output_file_name, 'w')
            print 'writing', output_file_name
            for sentence in sentences_per_cand[cand]:
                output_file.write(sentence)
                output_file.write('\n')

if __name__ == '__main__':
    main()
