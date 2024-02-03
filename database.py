import os
import mysql.connector as sql
from logger import logging

# Logging configuration
root = logging.getLogger("root")


def db_conn():
    host = os.environ.get("DB_HOST")
    user = os.environ.get("DB_USER")  # KY2
    password = os.environ.get("DB_PASS")
    database = os.environ.get("DB_NAME")
    tls_version = os.environ.get("DB_TLS")

    if not host or not user or not password or not database or tls_version not in ["TLSv1.2", "TLSv1.3"]:
        root.error("Missing database connection parameters")
        return None, None

        # Validate input from environment variables
    if not isinstance(host, str) or not isinstance(user, str) or not isinstance(password, str) or not isinstance(
            database, str) or not isinstance(tls_version, str):
        root.error("Invalid database connection parameters")
        return None, None

    try:
        mydb = sql.connect(
            host="127.0.0.1",
            user=os.environ.get("DB_USER"),  # KY2
            password=os.environ.get("DB_PASS"),
            database=os.environ.get("DB_NAME"),
            tls_versions=["TLSv1.3"]
        )
        mycursor = mydb.cursor()
        return mydb, mycursor
    except sql.InterfaceError as e:
        root.error(f"Error connecting to the database interface: {e}")
        return None, None
    except sql.DatabaseError as e:
        root.error(f"Error connecting to the database: {e}")
        return None, None


# DV7
def insert_user(u, fn, ln, e, a, p, s):
    db, cur = db_conn()
    if db and cur:
        try:
            query1 = """INSERT INTO accounts (uid, fname, lname, email, address, passw, salt, status, pwd_creation, acc_creation) VALUES (%s, %s, %s, 
                           %s, %s, %s, %s, %s, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())"""
            params = (u, fn, ln, e, a, p, s, "0")
            if not all(isinstance(param, str) for param in params) or u != "" or e != "":
                root.error("Invalid input parameters")
                return False
            cur.execute(query1, params)
            db.commit()
            ID = lookup_acc(u, None, 1)
            if ID:
                query2 = """INSERT INTO roles (role, id) VALUES (%s, %s) """
                params = ("user", ID[10])
                cur.execute(query2, params)
                db.commit()
                return True
            else:
                root.error("Failed to lookup account")
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def update_acc(ID, fname, lname, address, pas, s, i):
    db, cur = db_conn()
    if db and cur:
        try:
            if i == 1:
                query = "UPDATE accounts SET fname=%s, lname=%s, address=%s WHERE id=%s"
                params = (fname, lname, address, ID)
                cur.execute(query, params)
                db.commit()
                return True
            elif i == 2:
                query = "UPDATE accounts SET passw=%s, status=%s, pwd_creation=CURRENT_TIMESTAMP(), salt=%s WHERE id=%s"
                params = (pas, "0", s, ID)
                cur.execute(query, params)
                db.commit()
                return True
            else:
                return False
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def query_acc(ID, i):
    db, cur = db_conn()
    if db and cur:
        try:
            if i == 1:
                query = "SELECT * FROM accounts"
                cur.execute(query)
                rows = cur.fetchall()
                count = cur.rowcount
                return rows, count
            elif i == 2:
                db, cur = db_conn()
                query = "SELECT * FROM accounts WHERE id<>%s"
                params = (ID,)
                cur.execute(query, params)
                rows = cur.fetchall()
                return rows
            else:
                return False
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def lookup_acc(u, ID, i):
    db, cur = db_conn()
    if db and cur:
        try:
            if i == 1:
                query = "SELECT * FROM accounts WHERE uid=%s"
                params = (u,)
                cur.execute(query, params)
                rows = cur.fetchone()
                return rows
            elif i == 2:
                db, cur = db_conn()
                query = "SELECT * FROM accounts WHERE id=%s"
                params = (ID,)
                cur.execute(query, params)
                rows = cur.fetchone()
                return rows
            else:
                return False
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def delete_user(ID):
    db, cur = db_conn()
    if db and cur:
        try:
            query = "DELETE FROM accounts WHERE id=%s"
            params = (ID,)
            cur.execute(query, params)
            db.commit()
            cur.close()
            db.close()
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def update_role(ID, role):
    db, cur = db_conn()
    if db and cur:
        try:
            query = "UPDATE roles SET role=%s WHERE id=%s"
            params = (role, ID)
            cur.execute(query, params)
            db.commit()
            cur.close()
            db.close()
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def lookup_role(ID, i):
    db, cur = db_conn()
    if db and cur:
        try:
            params = (ID,)
            if i == 1:
                query = "SELECT * FROM roles WHERE id=%s"
                cur.execute(query, params)
                rows = cur.fetchone()
                return rows
            elif i == 2:
                query = "SELECT * FROM roles WHERE id<>%s"
                cur.execute(query, params)
                rows = cur.fetchall()
                return rows
            else:
                return False
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def lookup_status(ID):
    db, cur = db_conn()
    if db and cur:
        try:
            query = "SELECT * FROM accounts WHERE id=%s AND status=%s"
            params = (ID, "1",)
            cur.execute(query, params)
            rows = cur.fetchall()
            cur.close()
            db.close()
            return rows
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def update_status(ID):
    db, cur = db_conn()
    if db and cur:
        try:
            query = "UPDATE accounts SET status=%s WHERE id=%s"
            params = ("1", ID,)
            cur.execute(query, params)
            db.commit()
            cur.close()
            db.close()
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def insert_apppwd(ID, pa, appname):
    db, cur = db_conn()
    if db and cur:
        try:
            query = "INSERT INTO passwords (appname, pass, pwd_creation, id) VALUES (%s, %s, CURRENT_TIMESTAMP(), %s)"
            params = (appname, pa, ID)
            cur.execute(query, params)
            db.commit()
            cur.close()
            db.close()
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def update_apppwd(appid, ID, pa, appname):
    db, cur = db_conn()
    if db and cur:
        try:
            query = "Update passwords SET appname=%s, pass=%s, pwd_creation=CURRENT_TIMESTAMP() WHERE appid=%s AND id=%s"
            params = (appname, pa, appid, ID)
            cur.execute(query, params)
            db.commit()
            cur.close()
            db.close()
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def delete_apppwd(appid):
    db, cur = db_conn()
    if db and cur:
        try:
            query = "DELETE FROM passwords WHERE appid=%s"
            params = (appid,)
            cur.execute(query, params)
            db.commit()
            cur.close()
            db.close()
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def lookup_app(ID, appname, appid, i):
    db, cur = db_conn()
    if db and cur:
        try:
            if i == 1:
                query = "SELECT * FROM passwords WHERE id=%s AND appname=%s"
                params = (ID, appname,)
                cur.execute(query, params)
                rows = cur.fetchall()
                return rows
            elif i == 2:
                query = "SELECT * FROM passwords WHERE appid=%s"
                params = (appid,)
                cur.execute(query, params)
                rows = cur.fetchone()
                return rows
            else:
                return False
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def lookup_appperms(ID, appid, i):
    db, cur = db_conn()
    if db and cur:
        try:
            if i == 1:
                query = "SELECT * FROM permissions WHERE id=%s AND appid=%s"
                params = (ID, appid,)
                cur.execute(query, params)
                rows = cur.fetchall()
                return rows
            elif i == 2:
                query = """SELECT appid, permission, id FROM permissions 
                           WHERE appid IN (SELECT appid FROM passwords WHERE id=%s)
                           UNION
                           SELECT appid, permission, id FROM permissions 
                           WHERE appid IN (SELECT appid FROM permissions WHERE id=%s AND permission=%s)"""
                params = (ID, ID, 'e',)
                cur.execute(query, params)
                rows = cur.fetchall()
                return rows
            elif i == 3:
                query1 = """SELECT passw.appid, passw.id, passw.appname, passw.pass, passw.pwd_creation, perm.id, perm.permission
                            FROM passwords as passw
                            LEFT JOIN (SELECT * FROM permissions WHERE id=%s) AS perm ON passw.appid = perm.appid
                            WHERE perm.id=%s OR passw.id=%s
                            ORDER BY passw.appid"""
                params = (ID, ID, ID,)
                cur.execute(query1, params)
                rows = cur.fetchall()
                return rows
            else:
                return False
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")


def update_appperms(perm, ID, appid, i):
    db, cur = db_conn()
    if db and cur:
        try:
            if i == 1:
                rows = lookup_acc(None, ID, 2)
                app = lookup_app(None, None, appid, 2)
                if rows and app:
                    if i == 1:
                        resp = lookup_appperms(ID, appid, 1)
                        if resp:
                            query = "Update permissions SET permission=%s WHERE id=%s AND appid=%s"
                            params = (perm, ID, appid)
                            cur.execute(query, params)
                        else:
                            query = "INSERT INTO permissions(id, permission, appid) VALUES(%s, %s, %s)"
                            params = (ID, perm, appid)
                            cur.execute(query, params)
                        db.commit()
                        return True
                    elif i == 2:
                        query = "Update passwords SET id=%s WHERE appid=%s"
                        params = (rows[0][10], appid)
                        cur.execute(query, params)
                        db.commit()
                        return True
                    else:
                        return False
                else:
                    return False
        except sql.Error as e:
            db.rollback()
            root.error(f"Error executing SQL query: {e}")
        finally:
            cur.close()
            db.close()
    else:
        root.error("Failed to connect to the database")
