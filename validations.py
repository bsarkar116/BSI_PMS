from jsonschema import validate
import jsonschema


# referenced from http://donofden.com/blog/2020/03/15/How-to-Validate-JSON-Schema-using-Python

def validateJson(jsondata, schema):
    try:
        validate(instance=jsondata, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True
