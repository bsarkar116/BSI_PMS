from re import match
from json import loads
from validations import validate_json
from flask import Flask, Response, request, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_restful import Api, Resource
from schema import policySchema, userSchema, loginSchema, removeSchema
from tokens import create_token, verify_token
from policy import pass_retention, gen_policy
from database import lookup_user, del_user
from pms import adduser, compare_hash, update_pass, batch_add, batch_remove

app = Flask(__name__)
csrf = CSRFProtect(app)
api = Api(app, decorators=[csrf.exempt])  # Decorator to exempt CSRF protection for only REST APIs

# Constants
mime = "text/html"
reply = "Malformed data sent"

pass_retention()


# REST API resource referenced from https://www.youtube.com/watch?v=GMppyAPbLYk&t=1842s
class UserMgmt(Resource):
    def __init__(self):
        self.token = None
        self.role = None
        self.data = None
        self.passw = None
        self.output = None
        self.file = None

    def post(self):
        if 'auth-tokens' in request.headers:
            self.token = request.headers['auth-tokens']
        self.role = verify_token(self.token)
        if self.role == "admin":
            if match('/add/single', request.path):
                self.data = request.json
                isvalid = validate_json(self.data, userSchema)
                if isvalid:
                    response, self.passw = adduser(self.data['user'], self.data['role'], self.data['appid'])
                    if response:
                        return jsonify({"User": self.data['user'], "Pass": self.passw})
                    else:
                        return Response("Duplicate user", mimetype=mime, status=403)
                else:
                    return Response(reply, mimetype=mime, status=403)
            elif match('/add/multi', request.path):
                self.file = request.files['file']
                self.output = batch_add(self.file)
                if self.output.empty:
                    return Response(reply, mimetype=mime, status=403)
                else:
                    return Response(self.output.to_csv(), mimetype="text/csv", status=200)
        elif not self.role:
            return Response("Invalid token. Please generate new one.", mimetype=mime, status=403)
        else:
            return Response("User not authorized", mimetype=mime, status=403)

    def delete(self):
        if 'auth-tokens' in request.headers:
            self.token = request.headers['auth-tokens']
        self.role = verify_token(self.token)
        if self.role == "admin":
            if match('/del/single', request.path):
                self.data = request.json
                isvalid = validate_json(self.data, removeSchema)
                if isvalid:
                    response = del_user(self.data['user'])
                    if response:
                        return Response("User removed", mimetype=mime, status=200)
                    else:
                        return Response("User not found", mimetype=mime, status=403)
                else:
                    return Response(reply, mimetype=mime, status=403)
            elif match('/del/multi', request.path):
                self.file = request.files['file']
                self.output = batch_remove(self.file)
                if self.output.empty:
                    return Response(reply, mimetype=mime, status=403)
                else:
                    return Response(self.output.to_csv(), mimetype="text/csv", status=200)
        elif not self.role:
            return Response("Invalid token. Please generate new one.", mimetype=mime, status=403)
        else:
            return Response("User not authorized", mimetype=mime, status=403)


api.add_resource(UserMgmt, "/add/single", endpoint="add-single")
api.add_resource(UserMgmt, "/add/multi", endpoint="add-multi")
api.add_resource(UserMgmt, "/del/single", endpoint="del-single")
api.add_resource(UserMgmt, "/del/multi", endpoint="del-multi")


class Authenticate(Resource):
    def __init__(self):
        self.passw = None
        self.token = None
        self.data = None

    def get(self):
        self.data = request.json
        isvalid = validate_json(self.data, loginSchema)
        if isvalid:
            if compare_hash(self.data['user'], self.data['pass']):
                rows = lookup_user(self.data['user'])
                flag = rows[0][5]
                if flag == "1":
                    self.passw = update_pass(self.data['user'])
                    self.token = create_token(self.data['user'])
                    return jsonify({'token': self.token, 'Pass': self.passw, "Message": "New password generated"})
                elif flag == "0":
                    self.token = create_token(self.data['user'])
                    return jsonify({'token': self.token})
            else:
                return Response("Invalid User/Password", mimetype=mime, status=403)
        else:
            return Response(reply, mimetype=mime, status=403)


api.add_resource(Authenticate, "/auth", endpoint="auth")


class Policy(Resource):
    def __init__(self):
        self.token = None
        self.data = None
        self.file = None

    def post(self):
        if 'auth-tokens' in request.headers:
            self.token = request.headers['auth-tokens']
        role = verify_token(self.token)
        if role == "admin":
            self.file = request.files['file'].read()
            self.data = loads(self.file.decode())
            isvalid = validate_json(self.data, policySchema)
            if isvalid:
                gen_policy(self.data['Length'], self.data['Upper'], self.data['Lower'], self.data['Digits'], self.data['Special'], self.data['Age'])
                return Response("Policy updated", mimetype="text/html", status=200)
            else:
                return Response(reply, mimetype=mime, status=403)
        elif not role:
            return Response("Invalid token. Please generate new one.", mimetype=mime, status=403)
        else:
            return Response("User not authorized", mimetype=mime, status=403)


api.add_resource(Policy, "/policy", endpoint="policy")

if __name__ == "__main__":
    app.run(ssl_context=('cert.crt', 'cert.key'), host="localhost")
