import cherrypy
import json

class User_Controller:
    def __init__(self, database_controller):
        self.database_controller = database_controller

    def get_users(self):
        all_users = list(self.database_controller.users.values())

        output = {
            "result": "success",
            "users": all_users
        }

        return json.dumps(output)

    def post_users(self):
        # Read and parse the request body if method is POST, PUT or DELETE
        body = cherrypy.request.body.read().decode('utf-8')
        body = json.loads(body)

        output = {
            "result": "success"
        }

        if 'gender' not in body or 'age' not in body or 'occupation' not in body or 'zipcode' not in body:
            output["result"] = "error"

            return json.dumps(output)

        gender = body['gender']
        age = int(body['age'])
        occupation = int(body['occupation'])
        zipcode = body['zipcode']

        if not self.database_controller.users:
            user_id = 1
        else:
            user_id = max(self.database_controller.users) + 1

        self.database_controller.users[user_id] = {
            'id': user_id,
            'gender': gender,
            'age': age,
            'occupation': occupation,
            'zipcode': zipcode,
            'rated_movies': []
        }

        output["id"] = user_id

        return json.dumps(output)

    def delete_users(self):
        self.database_controller.users.clear()
        
        return json.dumps({"result": "success"})
    

    def get_user(self, user_id):
        output = {
            "result": "success",
        }
    
        user_id = int(user_id)
        user = self.database_controller.users.get(user_id)

        if not user:
            output["result"] = "error"

            return json.dumps(output)

        del user["rated_movies"]

        output.update(user)

        return json.dumps(output)
    

    def put_user(self, user_id):
        # Read and parse the request body if method is POST, PUT or DELETE
        body = cherrypy.request.body.read().decode('utf-8')
        body = json.loads(body)

        user_id = int(user_id)

        output = {
            "result": "success"
        }

        if 'gender' not in body or 'age' not in body or 'occupation' not in body or 'zipcode' not in body:
            output["result"] = "error"

            return json.dumps(output)
        
        gender = body['gender']
        age = int(body['age'])
        occupation = int(body['occupation'])
        zipcode = body['zipcode']
        
        self.database_controller.users[user_id] = {
            'id': user_id,
            'gender': gender,
            'age': age,
            'occupation': occupation,
            'zipcode': zipcode,
            'rated_movies': []
        }

        return json.dumps(output)

    def delete_user(self, user_id):
        user_id = int(user_id)

        if user_id in self.database_controller.users:
            del self.database_controller.users[user_id]
            return json.dumps({"result": "success"})
        else:
            return json.dumps({"result": "error"})
            