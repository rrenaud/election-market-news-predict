import random

import simplejson as json

import cand_sentences
import sentence_labeller

def debug_info_fn(learner_name, cand, date):
    return 'debug_info/' + cand + '.' + date + '.' + learner_name

class ModelDebugInfo:
    def __init__(self, learner_name, cand, date):
        self.learner_name = learner_name
        self.cand = cand
        self.date = date
        
        debug_info = json.load(open(debug_info_fn(learner_name, cand, date)))
        self.prediction = debug_info['prediction']
        self.scored_sentences = debug_info['scored_sentences']
        self.scored_words = debug_info['scored_words']
        self.actual = debug_info['actual']

    def render_debug_info(self, number):
        out = ''
        out += '<html>'
        out += '<meta http-equiv="Content-Type" '
        out += 'content="text/html;charset=utf-8" />'
        out += '<head><title>%s %s %s</title></head>\n' % (
            self.cand, self.date, self.learner_name)
        
        out += '<body>'
        out += 'prediction: %.4f<br>' % self.prediction
        out += 'actual: %.4f<br>' % self.actual
        out += '<form action="record" method="post">'
        out += '<input type="hidden" name="date" value="%s">' % self.date
        out += '<input type="submit">'
        out += '<table border=1>'
        out += '<tr><td width=450>resp</td><td width=50>score</td>'
        out += '<td>sentence</td></tr>\n'

        output_sentences = random.sample(self.scored_sentences, number)
        output_sentences.sort(key= lambda x: -abs(x[0]))

        label_reader = sentence_labeller.LabelledSentenceReader()
        for score, sentence in output_sentences:
            out += '<tr><td>'
            mentioned_cands = cand_sentences.mentioned_cands(sentence)
            sentence_hash = sentence_labeller.sentence_hash(sentence)
            ratings = label_reader.get_labels(self.date, sentence)
            for cand in sorted(mentioned_cands):
                name = '%s-%s' % (cand, sentence_hash)
                for option in ['great', 'good', 'neutral', 'bad', 'terrible']:
                    opt_id = '%s-%s' % (name, option)
                    checked = 'checked' if ratings[cand] == option else ''
                    out += ('<input type="radio" name="%s" value="%s" '
                            'id="%s" %s/>\n' % (name, option, opt_id, checked))
                    out += '<label for="%s">%s | </label>' % (opt_id, option)
                out += ' ' + cand.title() + '<br>\n'
            out += '</td>'
            out += '<td>%.4f</td><td>%s</td></tr>\n' % (
                score * 10, sentence)
        out += '</table>'
        out += '<input type="submit" >'
        out += '</form>'
        out += '</body>'
        out += '</html>'
        return out
