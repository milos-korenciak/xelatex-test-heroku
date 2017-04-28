
import atexit
import cherrypy
import report_core
import report_utils
import traceback


cherrypy.config.update({'environment': 'embedded'})
SERVER_ALIAS = "/reports"


# @cherrypy.expose
class ReportComposerService(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        return 'Make a POST request with valid report composer JSON!'

    def POST(self, output='json'):

# @cherrypy.expose
class ReportTemplatorService(object):
    exposed = True

    # def __init__(self):
    #     self.default_response = 'Make a POST request with valid JSON!'
    #
    # def index(self):
    #     return self.default_response
    # index.exposed = True

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        return 'Make a POST request with valid report templator JSON!'
    GET.exposed = True

    def POST(self, output='pdf'):
        valid_outputs = ['pdf', 'latex']
        raw_input = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        try:
            composer_obj = report_core.ReportTemplator(report_json=raw_input)
            if output == 'latex':
                return composer_obj.to_latex()
            elif output == 'pdf':
                cherrypy.response.headers['Content-Type'] = "application/pdf"
                return composer_obj.to_pdf()
            else:
                return "Valid 'output' parameter is one of {}!".format(valid_outputs)
        except Exception as e:
            cherrypy.response.status = "500 - Internal Server Error"
            return "Something went wrong, see the traceback message:\n{}".format(traceback.format_exc())
    POST.exposed = True


# if __name__ == '__main__':
conf = {
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.sessions.on': True,
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'text/plain')],
    }
}
# conf = None
# cherrypy.quickstart(ReportGeneratorWebService(), '/', conf)
# print 'import test'
cherrypy.tree.mount(Root(), script_name=SERVER_ALIAS + '/', config=None)
cherrypy.tree.mount(ReportComposerService(), script_name=SERVER_ALIAS + '/composer', config=conf)
cherrypy.tree.mount(ReportTemplatorService(), script_name=SERVER_ALIAS + '/templator', config=conf)

# server = cherrypy._cpserver.Server()
# server.socket_port = 8030

if __name__ == '__main__':  # for local testing
    import os
    # cherrypy.server.unsubscribe()  # very important gets rid of default.
    # server = cherrypy._cpserver.Server()
    # server.socket_port = 8030
    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'server.socket_port': int(os.getenv("PORT", 8030)),
                            })
    # cherrypy.engine.exit()
    cherrypy.engine.start()
    cherrypy.engine.block()

else:  # for apache wsgi_mod
    # if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
    if cherrypy.engine.state == 0:
        cherrypy.engine.start(blocking=False)
        atexit.register(cherrypy.engine.stop)

    # set required variable name for WSGI:
    application = cherrypy.tree