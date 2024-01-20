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
        "uid": {"type": "string", "pattern": "^[A-Za-z0-9]+[\._]?[A-Za-z0-9]$"},
        "fname": {"type": "string", "pattern": "^[A-Za-z0-9]+[\._]?[A-Za-z0-9]$"},
        "lname": {"type": "string", "pattern": "^[A-Za-z0-9]+[\._]?[A-Za-z0-9]$"},
        "email": {"type": "string", "pattern": "^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"},
        "address": {"type": "string"}
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
        "fname": {"type": "string", "pattern": "^[A-Za-z0-9]+[\._]?[A-Za-z0-9]$"},
        "lname": {"type": "string", "pattern": "^[A-Za-z0-9]+[\._]?[A-Za-z0-9]$"},
        "address": {"type": "string"}
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
        "uid": {"type": "string", "pattern": "^[A-Za-z0-9]+[\._]?[A-Za-z0-9]$"},
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
        "appname": {"type": "string"},
        "len": {"type": "integer", "minimum": 1, "maximum": 25},
    },
    "required": [
        "appname",
        "len"
    ]
}