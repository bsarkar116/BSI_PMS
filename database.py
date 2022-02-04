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
except:
    print("Missing config file")


def insert_user(u, p, r, appid):
    rows = lookup_user(u)
    if not rows:
        query = """INSERT INTO users (user, pass, role, creation, appid, status) VALUES (%s, %s, %s, 
        CURRENT_TIMESTAMP(), %s, %s) """
        mycursor.execute(query, (u, p, r, appid, "1"))
        mydb.commit()
        return True
    else:
        return False


def del_user(u):
    rows = lookup_user(u)
    if rows:
        query = """DELETE FROM users WHERE user=%s"""
        mycursor.execute(query, (u,))
        mydb.commit()
        return True
    else:
        return False


def query_all():
    query = """SELECT * FROM users"""
    mycursor.execute(query)
    rows = mycursor.fetchall()
    return rows


def lookup_user(u):
    query = """SELECT * FROM users WHERE user=%s"""
    mycursor.execute(query, (u,))
    rows = mycursor.fetchall()
    return rows


def updatep(u, pas):
    query = """UPDATE users SET pass=%s, status=%s, creation=CURRENT_TIMESTAMP() WHERE user=%s"""
    mycursor.execute(query, (pas, "0", u))
    mydb.commit()


def update_status(u):
    query = """UPDATE users SET status=%s WHERE user=%s"""
    mycursor.execute(query, ("1", u))
    mydb.commit()
