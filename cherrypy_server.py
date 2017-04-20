
import atexit
import cherrypy
import report_core
import report_utils
import traceback


# @cherrypy.expose
class Root(object):
    exposed = True

    def __init__(self):
        self.default_response = "Make a POST request with valid JSON to '{0}/composer' or '{1}/templator'!".format(SERVER_ALIAS, SERVER_ALIAS)

    def index(self):
        return self.default_response
    index.exposed = True

    # @cherrypy.tools.accept(media='text/plain')
    # def GET(self):
    #     return self.default_response
    #
    # def POST(self):
    #     return self.default_response

# @cherrypy.expose
class ReportComposerService(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        return 'Make a POST request with valid report composer JSON!'

    def POST(self, output='json'):
        valid_outputs = ['json', 'pdf', 'latex', 'config']
        raw_input = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        try:
            composer_obj = report_core.ReportComposer(request_json=raw_input)
            if output == 'json':
                return composer_obj.to_json_unicode()
            elif output == 'config':
                return composer_obj.configuration_to_unicode()
            elif output == 'latex':
                return composer_obj.to_latex()
            elif output == 'pdf':
                cherrypy.response.headers['Content-Type'] = "application/pdf"
                return composer_obj.to_pdf(remove_temp=False)
            else:
                return "Valid 'output' parameter is one of {}!".format(valid_outputs)
        except Exception as e:
            error_status = "500 - Internal Server Error"
            cherrypy.response.status = error_status
            # error_response = report_utils.make_error_response(error_status, "Something went wrong, see the error message:", e)
            # return error_response + '\n'
            return "Something went wrong, see the traceback message:\n{}".format(traceback.format_exc())


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
