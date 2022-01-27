from re import match
from jwt import encode
from json import load, loads
from validations import *
from datetime import datetime, timedelta
from flask import Flask, Response, request, jsonify
from flask_restful import Api, Resource
from schema import *
from misc import *
from pms import adduser, comparehash, passretention, updatepass, genpolicy

app = Flask(__name__)
api = Api(app)

try:
    with open("token.json") as json_file:
        tok = load(json_file)
except FileNotFoundError:
    print("Missing config file")


def createtoken(u):
    app.config["SECRET_KEY"] = str(tok["SECRET_KEY"])
    token = encode(
        {'user': u, 'exp': datetime.utcnow() + timedelta(minutes=10)},
        app.config['SECRET_KEY'])
    return token


# API resource referenced from https://www.youtube.com/watch?v=GMppyAPbLYk&t=1842s

class AddUser(Resource):
    def post(self):
        if match('/add/single', request.path):
            data = request.json
            isvalid = validateJson(data, userSchema)
            print(isvalid)
            if isvalid:
                response, passw = adduser(data['user'], data['role'], data['appid'])
                if response:
                    return jsonify({"User": data['user'], "Pass": passw})
                else:
                    return Response("Duplicate user", mimetype="text/html", status=403)
            else:
                return Response("Malformed data sent", mimetype="text/html", status=403)
        elif match('/add/multi', request.path):
            file = request.files['file']
            output = batchhandler(file)
            return Response(output.to_csv(), mimetype="text/csv", status=200)


api.add_resource(AddUser, "/add/single", endpoint="add-single")
api.add_resource(AddUser, "/add/multi", endpoint="add-multi")


class Authenticate(Resource):
    def get(self):
        data = request.json
        isvalid = validateJson(data, loginSchema)
        if isvalid:
            if comparehash(data['user'], data['pass']):
                if passretention():
                    passw = updatepass(data['user'])
                    token = createtoken(data['user'])
                    return jsonify({'token': token, 'Pass': passw, "Message": "Password has been updated"})
                else:
                    token = createtoken(data['user'])
                    return jsonify({'token': token})
            else:
                return Response("Invalid User/Password", mimetype="text/html", status=403)
        else:
            return Response("Malformed data sent", mimetype="text/html", status=403)


api.add_resource(Authenticate, "/auth", endpoint="auth")


class Policy(Resource):
    def post(self):
        file = request.files['file'].read()
        data = loads(file.decode())
        isvalid = validateJson(data, plicySchema)
        if isvalid:
            genpolicy(data['Length'], data['Upper'], data['Lower'], data['Digits'], data['Special'], data['Age'])
            return Response("Policy updated", mimetype="text/html", status=200)
        else:
            return Response("Malformed data sent", mimetype="text/html", status=403)


api.add_resource(Policy, "/policy", endpoint="policy")

if __name__ == "__main__":
    app.run(debug=True, ssl_context=('cert.crt', 'cert.key'), host="Localhost")
