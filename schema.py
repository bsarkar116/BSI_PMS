plicySchema = {
    "type": "object",
               "properties": {
                   "Length": {"type": "number"},
                   "Upper": {"type": "number"},
                   "Lower": {"type": "number"},
                   "Digits": {"type": "number"},
                   "Special": {"type": "number"},
                   "Age": {"type": "number"}
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
                  "user": {"type": "string"},
                  "role": {"type": "string"},
                  "appid": {"type": "string"}
              },
              "required": [
                  "user",
                  "role",
                  "appid"
              ]
            }

loginSchema = {
    "type": "object",
               "properties": {
                   "user": {"type": "string"},
                   "pass": {"type": "string"},
               },
               "required": [
                  "user",
                  "pass"
              ]
            }
