from flask import Flask, Response, request
from flask_restful import Api, Resource, reqparse
from pms import *
import pandas as pd

app = Flask(__name__)
api = Api(app)

# API resource referenced from https://www.youtube.com/watch?v=GMppyAPbLYk&t=1842s

single_args = reqparse.RequestParser()
single_args.add_argument("name", type=str, help="User name is missing", required=True)
single_args.add_argument("role", type=str, help="Desired role is missing", required=True)


class Single(Resource):
    def post(self):
        args = single_args.parse_args()
        response = ranpassgen(args['name'], args['role'])
        if response:
            rows = lookup(args['name'])
            return {"User": rows[0][0], "Pass": rows[0][1], "Role": rows[0][2]}, 200
        else:
            return Response("Duplicate user", mimetype="text/html", status=403)


class Batch(Resource):
    def post(self):
        file = request.files['file']
        df = pd.read_csv(file)
        templist = []
        df_new = df
        df_new["Password"] = " "
        for i in range(len(df)):
            result = ranpassgen(df.iloc[i, 0], df.iloc[i, 1])
            if result:
                rows = lookup(df.iloc[i, 0])
                templist.append(rows[0][1])
            else:
                templist.append("Duplicate user")
        df_new["Password"] = templist
        return Response(df_new.to_csv(), mimetype="text/csv", status=200)


api.add_resource(Single, "/single/")
api.add_resource(Batch, "/batch/")

if __name__ == "__main__":
    app.run(debug=True)
