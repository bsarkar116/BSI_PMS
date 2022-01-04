import mysql.connector

mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Intel4770@3.4"
)

mycursor = mydb.cursor()

# mycursor.execute("CREATE DATABASE password")
mycursor.execute("SHOW DATABASES")

for x in mycursor:
    print(x)
