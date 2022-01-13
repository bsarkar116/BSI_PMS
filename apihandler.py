# This is the main python script

import requests
from flask import Flask, Response, request
from flask_restful import Api, Resource, reqparse
from pms import *
import pandas as pd

app = Flask(__name__)
api = Api(app)

single_args = reqparse.RequestParser()
single_args.add_argument("name", type=str, help="User name is required", required=True)
single_args.add_argument("role", type=str, help="Desired role is required", required=True)


class Single(Resource):
    def post(self):
        args = single_args.parse_args()
        response = ranpassgen(args['name'], args['role'])
        if response:
            return Response("User Added", mimetype="text/html", status=200)
        else:
            return Response("User exists", mimetype="text/html", status=403)


file_args = reqparse.RequestParser()
file_args.add_argument("file", type=bytes)


class Batch(Resource):
    def post(self):
        file = request.files['file']
        df = pd.read_csv(file)
        for i in range(len(df)):
            ranpassgen(df.iloc[i, 0], df.iloc[i, 1])


api.add_resource(Single, "/single/")
api.add_resource(Batch, "/batch/")

if __name__ == "__main__":
    app.run(debug=True)
