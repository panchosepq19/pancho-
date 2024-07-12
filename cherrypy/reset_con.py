#!/usr/bin/env python3

import cherrypy
import json
from collections import defaultdict
import os
import ast


class Reset_Controller:
    def __init__(self, database_controller):
        self.database_controller = database_controller

    def reset(self):
        self.database_controller.movies = self.database_controller.load_movies()
        self.database_controller.users = self.database_controller.load_users()
        self.database_controller.ratings = self.database_controller.load_ratings()
        self.database_controller.images = self.database_controller.load_images()

        return json.dumps({"result": "success"})