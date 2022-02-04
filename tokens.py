import jwt
from datetime import datetime, timedelta
from database import lookup_user
from json import load

try:
    with open("token_key.json") as json_file:
        tok = load(json_file)
except:
    print("Missing config file")


# Referenced https://pyjwt.readthedocs.io/en/latest/index.html for jwt

def create_token(u):
    rows = lookup_user(u)
    token = jwt.encode({'user': u, 'role': rows[0][2], 'appid': rows[0][4], 'exp': datetime.utcnow() + timedelta(minutes=10)},
                       str(tok["SECRET_KEY"]))
    return token


def verify_token(token):
    try:
        if not token:
            return None
        else:
            payload = jwt.decode(token, str(tok["SECRET_KEY"]), algorithms=["HS256"], options={"require": ["exp"]})
            if not payload:
                return None
            else:
                role = payload['role']
        return role
    except (jwt.ExpiredSignatureError, jwt.MissingRequiredClaimError) as err:
        return None
