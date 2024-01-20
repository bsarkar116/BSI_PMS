import string
import secrets
import hashlib
import bcrypt
import schema
import validations
from policy import check_policy, read_pol, pass_retention, check_status, gen_policy, add_pol
from database import insert_user, del_user, insert_apppwd, lookup_role, query_acc,  \
    update_acc, update_apppwd, lookup_app, delete_apppwd, lookup_appperms, update_appperms, lookup_acc
from emailer import send_email
from schema import userSchema, loginSchema


def compare_hash(u, passw):
    rows = lookup_acc(u, "NULL", 1)
    if rows:
        salt = rows[0][6].encode()
        testpass = salt + passw.encode() + salt + passw.encode() + salt
        if hashlib.sha3_512(testpass).hexdigest() == rows[0][5]:
            return True
        else:
            return False
    else:
        return False


def random_gen():
    exclude = {"'", '"'}
    puncts = ''.join(ch for ch in string.punctuation if ch not in exclude)
    while True:
        p = read_pol()
        password = ''.join(
            secrets.choice(string.ascii_letters + string.digits + puncts) for i in range(p['Length']))
        if check_policy(password):
            break
    return password


# AH7, KY1
def hash_pwd(passw):
    salt = bcrypt.gensalt()
    dbpass = salt + passw.encode() + salt + passw.encode() + salt
    hashedpass = hashlib.sha3_512(dbpass).hexdigest()
    return hashedpass, salt


def add_user(u, fn, ln, e, a, i):
    user = {"uid": u, "fname": fn, "lname": ln, "email": e, "address": a}
    isValid = validations.validate_json(user, userSchema)
    if isValid:
        passw = random_gen()
        hpass, s = hash_pwd(passw)
        result = insert_user(u, fn, ln, e, a, hpass, s)
        send_email(u, e, passw, i)
        if result:
            return True
        else:
            return False
    else:
        return False


def update_user(ID, fn, ln, addr):
    info = {"fname": fn, "lname": ln, "address": addr}
    isValid = validations.validate_json(info, schema.profileSchema)
    if isValid:
        res = update_acc(ID, fn, ln, addr, "NULL", "NULL", 1)
        if res:
            return True
        else:
            return False
    else:
        return False


def delete_user(ID):
    res = del_user(ID)
    if res:
        return True
    else:
        return False


def update_accpass(ID, u, e, i):
    passw = random_gen()
    hpass, s = hash_pwd(passw)
    res = update_acc(ID, "NULL", "NULL", "NULL", hpass, s, 2)
    if res:
        send_email(u, e, passw, i)
        return True
    else:
        return False


def gen_apppass(lett, d, s, le):
    exclude = {"'", '"'}
    puncts = ''.join(ch for ch in string.punctuation if ch not in exclude)
    password = ""
    if lett and d and s:
        password = ''.join(
            secrets.choice(string.ascii_letters + string.digits + puncts) for i in range(le))
    elif lett and d and not s:
        password = ''.join(
            secrets.choice(string.ascii_letters + string.digits) for i in range(le))
    elif lett and not d and s:
        password = ''.join(
            secrets.choice(string.ascii_letters + puncts) for i in range(le))
    elif lett and not d and not s:
        password = ''.join(
            secrets.choice(string.ascii_letters) for i in range(le))
    return password


def add_apppwd(ID, appname, passw):
    result = insert_apppwd(ID, passw, appname)
    if result:
        return True
    else:
        return False


def upd_apppwd(appid, ID, appname, passw):
    result = update_apppwd(appid, ID, passw, appname)
    if result:
        return True
    else:
        return False


def del_apppwd(appid):
    delete_apppwd(appid)
