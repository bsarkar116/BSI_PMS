import os
import mysql.connector as sql


def db_conn():
    mydb = sql.connect(
        host="127.0.0.1",
        user=os.environ.get("DB_USER"),  # KY2
        password=os.environ.get("DB_PASS"),
        database=os.environ.get("DB_NAME"),
        tls_versions=["TLSv1.3"]
    )
    mycursor = mydb.cursor()
    return mydb, mycursor


# DV7
def insert_user(u, fn, ln, e, a, p, s):
    db, cur = db_conn()
    query1 = """INSERT INTO accounts (uid, fname, lname, email, address, passw, salt, status, pwd_creation, acc_creation) VALUES (%s, %s, %s, 
            %s, %s, %s, %s, %s, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()) """
    cur.execute(query1, (u, fn, ln, e, a, p, s, "0"))
    db.commit()
    ID = lookup_acc(u, "NULL", 1)
    query2 = """INSERT INTO roles (role, id) VALUES (%s, %s) """
    cur.execute(query2, ("user", ID[0][10]))
    db.commit()
    cur.close()
    db.close()


def update_acc(ID, fname, lname, address, pas, s, i):
    db, cur = db_conn()
    if i == 1:
        query = """UPDATE accounts SET fname=%s, lname=%s, address=%s WHERE id=%s"""
        cur.execute(query, (fname, lname, address, ID))
        db.commit()
        cur.close()
        db.close()
        return True
    elif i == 2:
        query = """UPDATE accounts SET passw=%s, status=%s, pwd_creation=CURRENT_TIMESTAMP(), salt=%s WHERE id=%s"""
        cur.execute(query, (pas, "0", s, ID))
        db.commit()
        cur.close()
        db.close()
    else:
        cur.close()
        db.close()
        return False


def query_acc(ID, i):
    db, cur = db_conn()
    if i == 1:
        query = """SELECT * FROM accounts"""
        cur.execute(query)
        rows = cur.fetchall()
        count = cur.rowcount
        cur.close()
        db.close()
        return rows, count
    elif i == 2:
        db, cur = db_conn()
        query = """SELECT * FROM accounts WHERE id<>%s"""
        cur.execute(query, (ID,))
        rows = cur.fetchall()
        cur.close()
        db.close()
        return rows
    else:
        cur.close()
        db.close()
        return False


def lookup_acc(u, ID, i):
    db, cur = db_conn()
    if i == 1:
        query = """SELECT * FROM accounts WHERE uid=%s"""
        cur.execute(query, (u,))
        rows = cur.fetchall()
        cur.close()
        db.close()
        return rows
    elif i == 2:
        db, cur = db_conn()
        query = """SELECT * FROM accounts WHERE id=%s"""
        cur.execute(query, (ID,))
        rows = cur.fetchall()
        cur.close()
        db.close()
        return rows
    else:
        cur.close()
        db.close()
        return False


def delete_user(ID):
    db, cur = db_conn()
    query = """DELETE FROM accounts WHERE id=%s"""
    cur.execute(query, (ID,))
    db.commit()
    cur.close()
    db.close()


def update_role(ID, role):
    db, cur = db_conn()
    query = """UPDATE roles SET role=%s WHERE id=%s"""
    cur.execute(query, (role, ID))
    db.commit()
    cur.close()
    db.close()


def lookup_role(ID, i):
    db, cur = db_conn()
    if i == 1:
        query = """SELECT * FROM roles WHERE id=%s"""
        cur.execute(query, (ID,))
        rows = cur.fetchall()
        cur.close()
        db.close()
        return rows
    elif i == 2:
        query = """SELECT * FROM roles WHERE id<>%s"""
        cur.execute(query, (ID,))
        rows = cur.fetchall()
        cur.close()
        db.close()
        return rows
    else:
        cur.close()
        db.close()
        return False


def lookup_status(ID):
    db, cur = db_conn()
    query = """SELECT * FROM accounts WHERE id=%s AND status=%s"""
    cur.execute(query, (ID, "1",))
    rows = cur.fetchall()
    cur.close()
    db.close()
    return rows


def update_status(ID):
    db, cur = db_conn()
    query = """UPDATE accounts SET status=%s WHERE id=%s"""
    cur.execute(query, ("1", ID,))
    db.commit()
    cur.close()
    db.close()


def insert_apppwd(ID, pa, appname):
    db, cur = db_conn()
    query = """INSERT INTO passwords (appname, pass, pwd_creation, id) VALUES (%s, %s, CURRENT_TIMESTAMP(), %s) """
    cur.execute(query, (appname, pa, ID))
    db.commit()
    cur.close()
    db.close()


def update_apppwd(appid, ID, pa, appname):
    db, cur = db_conn()
    query = """Update passwords SET appname=%s, pass=%s, pwd_creation=CURRENT_TIMESTAMP() WHERE appid=%s AND id=%s"""
    cur.execute(query, (appname, pa, appid, ID))
    db.commit()
    cur.close()
    db.close()


def delete_apppwd(appid):
    db, cur = db_conn()
    query = """DELETE FROM passwords WHERE appid=%s """
    cur.execute(query, (appid,))
    db.commit()
    cur.close()
    db.close()


def lookup_app(ID, appname, appid, i):
    db, cur = db_conn()
    if i == 1:
        query = """SELECT * FROM passwords WHERE id=%s AND appname=%s"""
        cur.execute(query, (ID, appname,))
        rows = cur.fetchall()
        cur.close()
        db.close()
        return rows
    elif i == 2:
        query = """SELECT * FROM passwords WHERE appid=%s"""
        cur.execute(query, (appid,))
        rows = cur.fetchall()
        cur.close()
        db.close()
        return rows
    else:
        cur.close()
        db.close()
        return False


def lookup_appperms(ID, appid, i):
    db, cur = db_conn()
    if i == 1:
        query = """SELECT * FROM permissions WHERE id=%s AND appid=%s"""
        cur.execute(query, (ID, appid,))
        rows = cur.fetchall()
        cur.close()
        db.close()
        return rows
    elif i == 2:
        query = """SELECT appid, permission, id FROM permissions 
                   WHERE appid IN (SELECT appid FROM passwords WHERE id=%s)
                   UNION
                   SELECT appid, permission, id FROM permissions 
                   WHERE appid IN (SELECT appid FROM permissions WHERE id=%s AND permission=%s)"""
        cur.execute(query, (ID, ID, 'e'))
        rows = cur.fetchall()
        cur.close()
        db.close()
        return rows
    elif i == 3:
        db, cur = db_conn()
        query1 = """SELECT passw.appid, passw.id, passw.appname, passw.pass, passw.pwd_creation, perm.id, perm.permission
                    FROM passwords as passw
                    LEFT JOIN (SELECT * FROM permissions WHERE id=%s) AS perm ON passw.appid = perm.appid
                    WHERE perm.id=%s OR passw.id=%s
                    ORDER BY passw.appid"""
        cur.execute(query1, (ID, ID, ID,))
        rows = cur.fetchall()
        cur.close()
        db.close()
        return rows
    else:
        cur.close()
        db.close()
        return False


def update_appperms(perm, ID, appid, i):
    db, cur = db_conn()
    rows = lookup_acc("NULL", ID, 2)
    app = lookup_app("NULL", "NULL", appid, 2)
    if rows and app:
        if i == 1:
            resp = lookup_appperms(ID, appid, 1)
            if resp:
                query = """Update permissions SET permission=%s WHERE id=%s AND appid=%s"""
                cur.execute(query, (perm, ID, appid))
                db.commit()
                cur.close()
                db.close()
                return True
            else:
                query = """INSERT INTO permissions(id, permission, appid) VALUES(%s, %s, %s)"""
                cur.execute(query, (ID, perm, appid))
                db.commit()
                cur.close()
                db.close()
                return True
        elif i == 2:
            query = """Update passwords SET id=%s WHERE appid=%s"""
            cur.execute(query, (rows[0][10], appid))
            db.commit()
            cur.close()
            db.close()
            return True
        else:
            cur.close()
            db.close()
            return False
    else:
        cur.close()
        db.close()
        return False
