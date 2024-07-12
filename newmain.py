#!/usr/bin/env python3

import cherrypy
import json
from collections import defaultdict
import os
import ast

# add imports
from data_con import Data_Controller
from movie_con import Movie_Controller
from ratings_con import Ratings_Controller
from recs_con import Reccomendations_Controller
from reset_con import Reset_Controller
from user_con import User_Controller

# first add a controller and handler for OPTIONS calls
class optionsController:
        def OPTIONS(self, *args, **kwargs):
                return ""

# next create this CORS function in main.py to add response headers
def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET, PUT, POST, DELETE, OPTIONS"
    cherrypy.response.headers["Access-Control-Allow-Credentials"] = "true"

# next connect OPTIONS requests to all resources, here are just a couple samples to get you started
    # default OPTIONS handler for CORS, all direct to the same place
    #dispatcher.connect('movie_options', '/movies/:movie_id', controller=optionsController, action = 'OPTIONS', conditions=dict(method=['OPTIONS']))
    #dispatcher.connect('movie_index_options', '/movies/', controller=optionsController, action = 'OPTIONS', conditions=dict(method=['OPTIONS']))

    

def begin():
    my_data = Data_Controller()
    movie_con = Movie_Controller(my_data)
    ratings_con = Ratings_Controller(my_data)
    recs_con = Reccomendations_Controller(my_data)
    reset_con = Reset_Controller(my_data)
    user_con = User_Controller(my_data)

    # add controllers and pass in data controller
    dispatcher = cherrypy.dispatch.RoutesDispatcher()

    # movies -- CHANGE CONTROLLERS   
    dispatcher.connect('get_movies', '/movies/', controller=movie_con, action='get_movies', conditions=dict(method=['GET']))
    dispatcher.connect('post_movies', '/movies/', controller=movie_con, action='post_movies', conditions=dict(method=['POST']))
    dispatcher.connect('delete_movies', '/movies/', controller=movie_con, action='delete_movies', conditions=dict(method=['DELETE']))

    # movie/: id    
    dispatcher.connect('get_movies_id', '/movies/:movie_id', controller=movie_con, action='get_movie_id', conditions=dict(method=['GET']))
    dispatcher.connect('put_movies_id', '/movies/:movie_id', controller=movie_con, action='put_movie_id', conditions=dict(method=['PUT']))
    dispatcher.connect('delete_movies_id', '/movies/:movie_id', controller=movie_con, action='delete_movies_id', conditions=dict(method=['DELETE']))

    # /USERS/    
    dispatcher.connect('get_users', '/users/', controller=user_con, action='get_users', conditions=dict(method=['GET']))
    dispatcher.connect('post_users', '/users/', controller=user_con, action='post_users', conditions=dict(method=['POST']))
    dispatcher.connect('delete_users', '/users/', controller=user_con, action='delete_users', conditions=dict(method=['DELETE']))

    # /USERS/:ID
    dispatcher.connect('get_user', '/users/:user_id', controller=user_con, action='get_user', conditions=dict(method=['GET']))
    dispatcher.connect('put_user', '/users/:user_id', controller=user_con, action='put_user', conditions=dict(method=['PUT']))
    dispatcher.connect('delete_user', '/users/:user_id', controller=user_con, action='delete_user', conditions=dict(method=['DELETE']))

    # RECOMENDATIONS   
    dispatcher.connect('delete_recommendations', '/recommendations/', controller=recs_con, action='delete_recommendations', conditions=dict(method=['DELETE']))

    # RECOMENDATIONS/:USER_ID    
    dispatcher.connect('get_recomendations_id', '/recommendations/:user_id', controller=recs_con, action='get_recommendations_id', conditions=dict(method=['GET']))
    dispatcher.connect('put_recomendations_id', '/recommendations/:user_id', controller=recs_con, action='put_recommendations_id', conditions=dict(method=['PUT']))
    
    #RATINGS
    dispatcher.connect('ratings', '/ratings/:movie_id', controller=ratings_con, action='ratings', conditions=dict(method=['GET']))

    #RESET
    dispatcher.connect('reset', '/reset/', controller=reset_con, action='reset', conditions=dict(method=['PUT']))

    dispatcher.connect('movie_options', '/movies/', controller=optionsController, action = 'OPTIONS', conditions=dict(method=['OPTIONS']))
    dispatcher.connect('movie_options_slug', '/movies/:movie_id', controller=optionsController, action = 'OPTIONS', conditions=dict(method=['OPTIONS']))
    dispatcher.connect('users_options', '/users/', controller=optionsController, action = 'OPTIONS', conditions=dict(method=['OPTIONS']))
    dispatcher.connect('users_options_slug', '/users/:user_id', controller=optionsController, action = 'OPTIONS', conditions=dict(method=['OPTIONS']))
    dispatcher.connect('ratings_options', '/ratings/', controller=optionsController, action = 'OPTIONS', conditions=dict(method=['OPTIONS']))
    dispatcher.connect('reset_options', '/reset/', controller=optionsController, action = 'OPTIONS', conditions=dict(method=['OPTIONS']))
    dispatcher.connect('reset_options_slug', '/reset/:movie_id', controller=optionsController, action = 'OPTIONS', conditions=dict(method=['OPTIONS']))
    dispatcher.connect('recommendations_options', '/recommendations/', controller=optionsController, action = 'OPTIONS', conditions=dict(method=['OPTIONS']))
    dispatcher.connect('recommendations_options_slug', '/recommendations/:user_id', controller=optionsController, action = 'OPTIONS', conditions=dict(method=['OPTIONS']))
    

    conf = {
        "global": {
            "server.socket_host": "student04.cse.nd.edu",
            "server.socket_port": 51005
        },
        "/": {
            "request.dispatch": dispatcher,
            "tools.CORS.on": True  
        }
    }

    cherrypy.config.update(conf)
    app = cherrypy.tree.mount(None, config=conf)
    cherrypy.tools.CORS = cherrypy.Tool('before_finalize', CORS)
    cherrypy.quickstart(app)
    



if __name__ == '__main__':
    begin()