from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

class Employees(Resource):
    def get(self):
        return "Employees page"


class Tracks(Resource):
    def get(self):
        return "Tracks page"


class Employees_Name(Resource):
    def get(self, employee_id):
        return "Employees_Name " + employee_id


api.add_resource(Employees, '/employees') # Route_1
api.add_resource(Tracks, '/tracks') # Route_2
api.add_resource(Employees_Name, '/employees/<employee_id>') # Route_3


if __name__ == '__main__':
     app.run(port='5002')
