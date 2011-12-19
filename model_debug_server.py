import os
import sys
import web
import urlparse

import model_debug_info
import sentence_labeller

urls = (
    '/', 'IndexPage',
    '/debug', 'DebugPage',
    '/record', 'RecordPage'
)

class IndexPage:
    def GET(self):
        out = ''
        out += '<html><head><title>Debug Model Server</title></head>\n'
        out += '<body><table>'
        debug_instances = []
        for fn in os.listdir('debug_info'):
            cand, date, learner_name = fn.split('.')
            debug_instances.append((cand, date, learner_name))
        debug_instances.sort()
        for cand, date, learner_name in debug_instances:
            out += (
                '<tr><td><a href='
                '"debug?cand=%(cand)s&date=%(date)s&model=%(model)s">'
                '%(cand)s</td></a>'
                '<td>%(date)s</td>'
                '<td>%(model)s</td></tr></a>\n' % {'cand': cand,
                                                   'date': date,
                                                   'model': learner_name})
        out += '</table></body></html>'
        return out

class DebugPage:
    def GET(self):
        query_dict = dict(urlparse.parse_qsl(web.ctx.env['QUERY_STRING']))
        model_debug = model_debug_info.ModelDebugInfo(
            query_dict['model'], query_dict['cand'], query_dict['date'])
        return model_debug.render_debug_info(100)

class RecordPage:
    def POST(self):
        data = web.data()
        return sentence_labeller.record_data(data)

app = web.application(urls, globals())
if __name__ == '__main__':
    app.run()
