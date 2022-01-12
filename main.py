# This is the main python script

from flask import Flask, Response
from flask_restful import Api, Resource
from pms import *

app = Flask(__name__)
api = Api(app)


class Password(Resource):
    def put(self, user):
        response = ranpassgen(user)
        if response:
            return Response("User Added", mimetype="text/html", status=200)
        else:
            return Response("User exists", mimetype="text/html", status=403)


api.add_resource(Password, "/passgen/<string:user>")

if __name__ == "__main__":
    app.run(debug=True)
