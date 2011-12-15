# coding=utf-8

import unittest2 as unittest

import nltk.data
import cand_sentences as cs

class TestNormalizeToken(unittest.TestCase):
    def testNormalizeToken(self):
        self.assertEquals(cs.normalize_token('Paul'), 'paul')
        self.assertEquals(cs.normalize_token("Romney's"), "romney")
        self.assertEquals(cs.normalize_token('Fo.'), 'fo')
        self.assertEquals(cs.normalize_token('Bachmann,'), 'bachmann')

class ExtractCandidateSentences(unittest.TestCase):
    def setUp(self):
        self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    def extract(self, text):
        return dict(cs.extract_cand_sentences(text, self.sent_tokenizer))

    def testExtractSentences1(self):
        text = """
Herman Cain offered a stern denial of allegations, raised in a Sunday Politico story.
"""
        extracted = {'cain': set([
"""Herman Cain offered a stern denial of allegations, raised in a Sunday Politico story.""",
])}
        self.assertEquals(extracted, self.extract(text))

    def testExtractSentences2(self):
        self.maxDiff = None
        text = """"Neveraaaaaaaaa sexually harassed anyone,” Cain said. “And I say falsely because it turned out after the investigation to be baseless.  The people mentioned in that article were the ones who would be aware of any misdoings, and they have attested to my integrity and my character. It is totally baseless, and totally false, never have I committed any sort of sexual harassment.”
"""
        extracted = {'cain': set([
""""Neveraaaaaaaaa sexually harassed anyone,” Cain said."""])}
        self.assertEquals(extracted, self.extract(text))

    def testExtractSentences3(self):
        self.maxDiff = None
        s1 = """Paul told CNN's "State of the Union" that Romney has been "pretty smooth" in responding to criticism over changing his position on issues."""
        s2 = """He made a point of noting that, unlike Romney, "they haven't challenged me for flip-flopping, so I'm very proud of that."""
        text =  s1 + ' ' + s2
        extracted = {'romney': set([s1, s2]), 'paul': set([s1])}
        self.assertEquals(extracted, self.extract(text))

    def testExtractSentences4(self):
        text = "Paul said Paul likes chicken a lot great than 50 chars."
        extracted = {'paul': set([text])}
        self.assertEquals(extracted, self.extract(text))
        
if __name__ == '__main__':
    unittest.main()
