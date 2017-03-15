import sys
sys.stdout = sys.stderr

import atexit
import threading
import cherrypy

cherrypy.config.update({'environment': 'embedded'})

if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)

class Root(object):
    def index(self):
        return 'Hello World!'
    index.exposed = True


conf = {
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.sessions.on': True,
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'text/plain')],
    }
}

SERVER_ALIAS = "/reports"
# cherrypy.tree.mount(Root(), script_name='/', config=conf)
cherrypy.tree.mount(Root(), script_name= SERVER_ALIAS + '/', config=None)
application = cherrypy.tree

# application = cherrypy.Application(Root(), script_name=None, config=None)