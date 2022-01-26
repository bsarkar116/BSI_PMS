import re
import jwt
import json
import datetime
from flask import Flask, Response, request, jsonify
from flask_restful import Api, Resource, reqparse
from pms import ranpassgen, comparehash
import pandas as pd

app = Flask(__name__)
api = Api(app)

try:
    with open('token.json') as json_file:
        tok = json.load(json_file)
except FileNotFoundError:
    print("Missing config file")

# API resource referenced from https://www.youtube.com/watch?v=GMppyAPbLYk&t=1842s

single_args = reqparse.RequestParser()
single_args.add_argument("user", type=str, help="User name is missing", required=True)
single_args.add_argument("role", type=str, help="Desired role is missing", required=True)


class AddUser(Resource):
    def post(self):
        if re.match('/add/single', request.path):
            args = single_args.parse_args()
            response, passw = ranpassgen(args['user'], args['role'])
            if response:
                return {"User": args['user'], "Pass": passw}, 200
            else:
                return Response("Duplicate user", mimetype="text/html", status=403)
        elif re.match('/add/multi', request.path):
            file = request.files['file']
            df = pd.read_csv(file)
            templist = []
            df_new = df.drop("Role", axis=1)
            for i in range(len(df)):
                result, passw = ranpassgen(df.iloc[i, 0], df.iloc[i, 1])
                if result:
                    templist.append(passw)
                else:
                    templist.append("Duplicate user")
            df_new["Password"] = templist
            return Response(df_new.to_csv(), mimetype="text/csv", status=200)


api.add_resource(AddUser, "/add/single", endpoint="add-single")
api.add_resource(AddUser, "/add/multi", endpoint="add-multi")

auth_args = reqparse.RequestParser()
auth_args.add_argument("user", type=str, help="User name is missing", required=True)
auth_args.add_argument("pass", type=str, help="Password is missing", required=True)

app.config['SECRET_KEY'] = str(tok["SECRET_KEY"])


class Authenticate(Resource):
    def get(self):
        args = auth_args.parse_args()
        if comparehash(args['user'], args['pass']):
            token = jwt.encode(
                {'user': args['user'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)},
                app.config['SECRET_KEY'])
            return jsonify({'token': token})
        else:
            return Response("Invalid User/Password", mimetype="text/html", status=404)


api.add_resource(Authenticate, "/auth", endpoint="auth")

if __name__ == "__main__":
    app.run(debug=True, ssl_context=('cert.crt', 'cert.key'), host="Localhost")
