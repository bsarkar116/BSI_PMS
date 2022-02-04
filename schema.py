policySchema = {
    "type": "object",
               "properties": {
                   "Length": {"type": "integer", "minimum": 1},
                   "Upper": {"type": "integer", "minimum": 0},
                   "Lower": {"type": "integer", "minimum": 0},
                   "Digits": {"type": "integer", "minimum": 0},
                   "Special": {"type": "integer", "minimum": 0},
                   "Age": {"type": "integer", "minimum": 1}
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
                  "user": {"type": "string", "pattern": "^[A-Za-z0-9]+[\._]?[A-Za-z0-9]+[@]acme.com$"},
                  "role": {"type": "string", "enum": ["user", "admin"]},
                  "appid": {"type": "string", "pattern": "^a+[0-9]$"}
              },
              "required": [
                  "user",
                  "role",
                  "appid"
              ]
            }

removeSchema = {
    "type": "object",
              "properties": {
                  "user": {"type": "string", "pattern": "^[A-Za-z0-9]+[\._]?[A-Za-z0-9]+[@]acme.com$"}
              },
              "required": [
                  "user"
              ]
            }

loginSchema = {
    "type": "object",
               "properties": {
                   "user": {"type": "string", "pattern": "^[A-Za-z0-9]+[\._]?[A-Za-z0-9]+[@]acme.com$"},
                   "pass": {"type": "string"},
               },
               "required": [
                  "user",
                  "pass"
              ]
            }
