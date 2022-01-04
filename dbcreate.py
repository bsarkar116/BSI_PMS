import mysql.connector
import json

with open('dbcreds.json') as json_file:
    data = json.load(json_file)
user = str(data["User"])
passw = str(data["Password"])
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user=user,
    password=passw
)

mycursor = mydb.cursor()

# mycursor.execute("CREATE DATABASE password")
mycursor.execute("SHOW DATABASES")

for x in mycursor:
    print(x)
