import json
import mysql.connector as sql

try:
    with open('dbcreds.json') as db_file:
        data = json.load(db_file)
    usr = str(data["User"])
    passw = str(data["Password"])
    db = str(data["Database"])
    mydb = sql.connect(
        host="127.0.0.1",
        user=usr,
        password=passw,
        database=db
    )
    mycursor = mydb.cursor()
except FileNotFoundError:
    print("No file found with database information")


def insertuser(u, p, r):
    rows = lookup(u)
    if not rows:
        query = """INSERT INTO users (user, pass, role, creation) VALUES (%s, %s, %s, CURRENT_DATE())"""
        mycursor.execute(query, (u, p, r))
        mydb.commit()
        return True
    else:
        return False


def lookup(u):
    query = """SELECT * FROM users WHERE user=%s"""
    mycursor.execute(query, (u,))
    rows = mycursor.fetchall()
    return rows

