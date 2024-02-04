policySchema = {
    "type": "object",
    "properties": {
        "Length": {"type": "integer", "minimum": 6, "maximum": 30},
        "Upper": {"type": "integer", "minimum": 1},
        "Lower": {"type": "integer", "minimum": 1},
        "Digits": {"type": "integer", "minimum": 1},
        "Special": {"type": "integer", "minimum": 1},
        "Age": {"type": "integer", "minimum": 10, "maximum": 60}
    },
    "required": [
        "Length",
        "Upper",
        "Lower",
        "Digits",
        "Special",
        "Age"
    ]
}

userSchema = {
    "type": "object",
    "properties": {
        "uid": {"type": "string", "pattern": "^(?![nN][uU][lL]{2}$)\\s*\\S.*"},
        "fname": {"type": "string", "pattern": "^(?![nN][uU][lL]{2}$)\\s*\\S.*"},
        "lname": {"type": "string", "pattern": "^(?![nN][uU][lL]{2}$)\\s*\\S.*"},
        "email": {"type": "string", "pattern": "^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"},
        "address": {"type": "string", "pattern": "^(?![nN][uU][lL]{2}$)\\s*\\S.*"}
    },
    "required": [
        "uid",
        "fname",
        "lname",
        "email",
        "address"
    ]
}

profileSchema = {
    "type": "object",
    "properties": {
        "fname": {"type": "string", "pattern": "^(?![nN][uU][lL]{2}$)\\s*\\S.*"},
        "lname": {"type": "string", "pattern": "^(?![nN][uU][lL]{2}$)\\s*\\S.*"},
        "address": {"type": "string", "pattern": "^(?![nN][uU][lL]{2}$)\\s*\\S.*"}
    },
    "required": [
        "fname",
        "lname",
        "address"
    ]
}


loginSchema = {
    "type": "object",
    "properties": {
        "uid": {"type": "string", "pattern": "^(?![nN][uU][lL]{2}$)\\s*\\S.*"},
        "pass": {"type": "string"},
    },
    "required": [
        "uid",
        "pass"
    ]
}


appSchema = {
    "type": "object",
    "properties": {
        "appname": {"type": "string", "pattern": "^(?![nN][uU][lL]{2}$)\\s*\\S.*"},
        "len": {"type": "integer", "minimum": 1, "maximum": 25},
    },
    "required": [
        "appname",
        "len"
    ]
}