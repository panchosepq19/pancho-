#!/usr/bin/env python3

import cherrypy
import json
from collections import defaultdict
import os
import ast

class Reccomendations_Controller:
    def __init__(self, database_controller):
        self.database_controller = database_controller
   
    def get_recommendations_id(self, user_id):
        user_id = int(user_id)
        recommendation = self.database_controller.recommend_movie_for_user(user_id)

        output = {
            "result": "success"
        }

        if not recommendation:
            output["result"] = "error"

            return json.dumps(output)
        
        output["user_id"] = user_id
        output["movie_id"] = recommendation

        return json.dumps(output)
    
    def put_recommendations_id(self, user_id):
        # Read and parse the request body if method is POST, PUT or DELETE
        body = cherrypy.request.body.read().decode('utf-8')
        body = json.loads(body)

        output = {
            "result": "success"
        }

        if not "movie_id" in body or not "rating" in body:
            output["result"] = "error"

            return json.dumps(output)

        user_id = int(user_id)
        movie_id = int(body['movie_id'])
        rating = int(body['rating'])
        
        self.database_controller.add_or_update_rating(user_id, movie_id, rating)

        return json.dumps(output)
    
    def delete_recommendations(self):
        self.database_controller.ratings.clear()

        for user in self.database_controller.users.values():
            user['rated_movies'].clear()

        return json.dumps({"result": "success"})