#!/usr/bin/python

# Extract sentences containing exactly one candidate name from the text 
# articles for a given day.

import os
import collections
import re

import candidate_info

TEXT_RESULTS_DIR = 'text_results/'

sentence_split_re = re.compile('\.|\\n\\n')
punct_chars_re = re.compile("[,\\.']")

def normalize_token(token):
    split = re.sub(punct_chars_re, ' ', token.lower()).split()
    if len(split) > 0:
        return split[0]
    return ''

def clean_sentence(sentence):
    return ' '.join(sentence.split()).strip()

def extract_cand_sentences(contents):
    ret = collections.defaultdict(list)
    sentences = sentence_split_re.split(contents)
    for sentence in sentences:
        tokens = sentence.split()
        seen_cands = set()
        for token in tokens:
            norm_token = normalize_token(token)
            if norm_token in candidate_info.candidate_last_names:
                seen_cands.add(norm_token)
            if len(seen_cands) > 1:
                break
        else:
            if len(seen_cands) == 1:
                ret[iter(seen_cands).next()].append(clean_sentence(sentence))
    return ret

def extract_cand_sentences_in_files(files):
    ret = collections.defaultdict(list)
    for fn in files:
        per_article_sentences = extract_cand_sentences(
            open(TEXT_RESULTS_DIR + fn).read())
        for cand in per_article_sentences:
            ret[cand].extend(per_article_sentences[cand])
    return ret

def main():
    files_to_process = os.listdir(TEXT_RESULTS_DIR)
    files_by_date = collections.defaultdict(list)
    for fn in files_to_process:
        files_by_date[fn[:8]].append(fn)

    for date in files_by_date:
        sentences_per_cand = extract_cand_sentences_in_files(
            files_by_date[date])
        for cand in sentences_per_cand:
            output_file = open('sentences/' + cand + '.' + date, 'w')
            for sentence in sentences_per_cand[cand]:
                output_file.write(sentence)
                output_file.write('\n')

if __name__ == '__main__':
    main()
