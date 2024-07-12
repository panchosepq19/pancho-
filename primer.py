#!/usr/bin/env python3

import cherrypy

class MyController:
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def GET (self):
        return {"result": "success", "name": "Francisco Septien Quintana"}

    
mycont = MyController()

dispacher = cherrypy.dispatch.RoutesDispatcher()

dispacher.connect('nameg', '/name/', controller=mycont, action='GET', conditions=dict(method=['GET']))

conf = {'global': {'server.socket_host': 'student04.cse.nd.edu', 
                   'server.socket_port': 52002},
        '/':{'request.dispatch': dispacher} }

cherrypy.config.update(conf)
app = cherrypy.tree.mount(None, config=conf)
cherrypy.quickstart(app)