# This is the main python script

from flask import Flask
from flask_restful import Api, Resource
import pms

app = Flask(__name__)
api = Api(app)


class Password(Resource):
    def put(self, user):
        pms.ranpassgen(user)
        return 200


api.add_resource(Password, "/passgen/<string:user>")

if __name__ == "__main__":
    app.run(debug=True, ssl_context='adhoc')



