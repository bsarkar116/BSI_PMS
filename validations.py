from re import fullmatch, compile

from jsonschema import validate
import jsonschema
import json
from schema import userSchema, removeSchema


# referenced from http://donofden.com/blog/2020/03/15/How-to-Validate-JSON-Schema-using-Python

def validate_json(jsondata, schema):
    try:
        validate(instance=jsondata, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True


def validate_csv(df):
    if "User" in df and "Role" in df and "AppID" in df:
        for i in range(len(df)):
            d = json.dumps({"user": df.iloc[i, 0], "role": df.iloc[i, 1], "appid": df.iloc[i, 2]})
            j = json.loads(d)
            out = validate_json(j, userSchema)
            if not out:
                return False
        return True
    elif "User" in df:
        for i in range(len(df)):
            d = json.dumps({"user": df.iloc[i, 0]})
            j = json.loads(d)
            out = validate_json(j, removeSchema)
            if not out:
                return False
        return True
    else:
        return False
