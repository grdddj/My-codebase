import os
import sqlite3

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

# Enabling CORS, to use this API everywhere
CORS(app)

# Initializting request parser and adding a key we will be using to transfer data
parser = reqparse.RequestParser()
parser.add_argument("hater_name")
parser.add_argument("lover_name")
parser.add_argument("other_person_name")
parser.add_argument("reason")

DB_LOCATION = "/var/www/myDB/myDB/hateyou.db"

# Creating a DB file, if it does not exist already
if not os.path.isfile(DB_LOCATION):
    with open(DB_LOCATION, "w"):
        pass

# Creating the tables if they do not already exist
conn = sqlite3.connect(DB_LOCATION)
c = conn.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS hates
             (id integer primary key, hater_name text, other_person_name text, reason text)"""
)
c.execute(
    """CREATE TABLE IF NOT EXISTS loves
             (id integer primary key, lover_name text, other_person_name text, reason text)"""
)
conn.commit()

conn.close()


class Hate(Resource):
    def post(self):
        conn = sqlite3.connect(DB_LOCATION)
        c = conn.cursor()

        # Parsing the parameters
        request_data = parser.parse_args()

        hater_name = request_data["hater_name"]
        other_person_name = request_data["other_person_name"]
        reason = request_data["reason"]

        try:
            c.execute(
                "INSERT INTO hates (hater_name, other_person_name, reason) VALUES (?, ?, ?)",
                (hater_name, other_person_name, reason),
            )
            conn.commit()
            conn.close()
            response = 200
        except:
            response = 500

        return response

    def get(self):
        conn = sqlite3.connect(DB_LOCATION)
        c = conn.cursor()

        c.execute("SELECT * FROM hates ORDER BY id DESC")
        result = c.fetchall()

        conn.close()
        return result


class Love(Resource):
    def post(self):
        conn = sqlite3.connect(DB_LOCATION)
        c = conn.cursor()

        # Parsing the parameters
        request_data = args = parser.parse_args()

        lover_name = request_data["lover_name"]
        other_person_name = request_data["other_person_name"]
        reason = request_data["reason"]

        try:
            c.execute(
                "INSERT INTO loves (lover_name, other_person_name, reason) VALUES (?, ?, ?)",
                (lover_name, other_person_name, reason),
            )
            conn.commit()
            conn.close()
            response = 200
        except:
            response = 500

        return response

    def get(self):
        conn = sqlite3.connect(DB_LOCATION)
        c = conn.cursor()

        c.execute("SELECT * FROM loves ORDER BY id DESC")
        result = c.fetchall()

        conn.close()
        return result


class HateLeaderboard(Resource):
    def get(self):
        conn = sqlite3.connect(DB_LOCATION)
        c = conn.cursor()

        c.execute(
            "SELECT other_person_name, COUNT(other_person_name) as count FROM hates GROUP BY other_person_name ORDER BY 2 DESC"
        )
        result = c.fetchall()

        conn.close()
        return result


class LoveLeaderboard(Resource):
    def get(self):
        conn = sqlite3.connect(DB_LOCATION)
        c = conn.cursor()

        c.execute(
            "SELECT other_person_name, COUNT(other_person_name) as count FROM loves GROUP BY other_person_name ORDER BY 2 DESC"
        )
        result = c.fetchall()

        conn.close()
        return result


api.add_resource(Love, "/love")
api.add_resource(Hate, "/hate")
api.add_resource(LoveLeaderboard, "/love_leaderboard")
api.add_resource(HateLeaderboard, "/hate_leaderboard")


if __name__ == "__main__":
    app.run(port="5002", debug=True)
