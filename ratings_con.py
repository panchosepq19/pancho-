    
#!/usr/bin/env python3

import json

class Ratings_Controller:
    def __init__(self, database_controller):
        self.database_controller = database_controller
    
    def ratings(self, movie_id):
        movie_id = int(movie_id)

        average_rating = self.database_controller.get_average_ratings().get(movie_id)

        output = {
            "result": "success"
        }

        if not average_rating:
            output["result"] = "error"
            return json.dumps(output)
        
        output["movie_id"] = movie_id
        output["rating"] = average_rating

        return json.dumps(output)
                
                