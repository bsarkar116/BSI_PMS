from jsonschema import validate
import jsonschema


def validate_json(jsondata, schema):
    try:
        validate(instance=jsondata, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True
