from re import match
from json import loads
from validations import validate_json
from flask import Flask, Response, request, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_restful import Api, Resource
from schema import plicySchema, userSchema, loginSchema, removeSchema
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
token = None

pass_retention()


# REST API resource referenced from https://www.youtube.com/watch?v=GMppyAPbLYk&t=1842s
class UserMgmt(Resource):
    def post(self):
        global token
        if 'auth-tokens' in request.headers:
            token = request.headers['auth-tokens']
        role = verify_token(token)
        if role == "admin":
            if match('/add/single', request.path):
                data = request.json
                isvalid = validate_json(data, userSchema)
                if isvalid:
                    response, passw = adduser(data['user'], data['role'], data['appid'])
                    if response:
                        return jsonify({"User": data['user'], "Pass": passw})
                    else:
                        return Response("Duplicate user", mimetype=mime, status=403)
                else:
                    return Response(reply, mimetype=mime, status=403)
            elif match('/add/multi', request.path):
                file = request.files['file']
                output = batch_add(file)
                if output.empty:
                    return Response(reply, mimetype=mime, status=403)
                else:
                    return Response(output.to_csv(), mimetype="text/csv", status=200)
        elif not role:
            return Response("Invalid token. Please generate new one.", mimetype=mime, status=403)
        else:
            return Response("User not authorized", mimetype=mime, status=403)

    def delete(self):
        global token
        if 'auth-tokens' in request.headers:
            token = request.headers['auth-tokens']
        role = verify_token(token)
        if role == "admin":
            if match('/del/single', request.path):
                data = request.json
                isvalid = validate_json(data, removeSchema)
                if isvalid:
                    response = del_user(data['user'])
                    if response:
                        return Response("User removed", mimetype=mime, status=200)
                    else:
                        return Response("User not found", mimetype=mime, status=403)
                else:
                    return Response(reply, mimetype=mime, status=403)
            elif match('/del/multi', request.path):
                file = request.files['file']
                output = batch_remove(file)
                if output.empty:
                    return Response(reply, mimetype=mime, status=403)
                else:
                    return Response(output.to_csv(), mimetype="text/csv", status=200)
        elif not role:
            return Response("Invalid token. Please generate new one.", mimetype=mime, status=403)
        else:
            return Response("User not authorized", mimetype=mime, status=403)


api.add_resource(UserMgmt, "/add/single", endpoint="add-single")
api.add_resource(UserMgmt, "/add/multi", endpoint="add-multi")
api.add_resource(UserMgmt, "/del/single", endpoint="del-single")
api.add_resource(UserMgmt, "/del/multi", endpoint="del-multi")


class Authenticate(Resource):
    def get(self):
        data = request.json
        isvalid = validate_json(data, loginSchema)
        if isvalid:
            if compare_hash(data['user'], data['pass']):
                rows = lookup_user(data['user'])
                flag = rows[0][5]
                if flag == "1":
                    passw = update_pass(data['user'])
                    t = create_token(data['user'])
                    return jsonify({'token': t, 'Pass': passw, "Message": "New password generated"})
                elif flag == "0":
                    t = create_token(data['user'])
                    return jsonify({'token': t})
            else:
                return Response("Invalid User/Password", mimetype=mime, status=403)
        else:
            return Response(reply, mimetype=mime, status=403)


api.add_resource(Authenticate, "/auth", endpoint="auth")


class Policy(Resource):
    def post(self):
        global token
        if 'auth-tokens' in request.headers:
            token = request.headers['auth-tokens']
        role = verify_token(token)
        if role == "admin":
            file = request.files['file'].read()
            data = loads(file.decode())
            isvalid = validate_json(data, plicySchema)
            if isvalid:
                gen_policy(data['Length'], data['Upper'], data['Lower'], data['Digits'], data['Special'], data['Age'])
                return Response("Policy updated", mimetype="text/html", status=200)
            else:
                return Response(reply, mimetype=mime, status=403)
        elif not role:
            return Response("Invalid token. Please generate new one.", mimetype=mime, status=403)
        else:
            return Response("User not authorized", mimetype=mime, status=403)


api.add_resource(Policy, "/policy", endpoint="policy")

if __name__ == "__main__":
    app.run(debug=True, ssl_context=('cert.crt', 'cert.key'), host="localhost")
