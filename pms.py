import string
import secrets
import hashlib
import requests
import bcrypt
from policy import *
from database import insertuser, lookupuser, updatep


def callhibp(p):
    flag = 0
    m = hashlib.sha1(p.encode('utf8')).hexdigest()
    query = "https://api.pwnedpasswords.com/range/" + m[:5]
    response = requests.get(query)
    for line in response.text.splitlines():  #
        a, b = line.split(":", 1)
        if m[5:] == a.lower():
            flag = 1
            break
    return flag


def hashing(passw):  # referenced from https://stackoverflow.com/questions/8870190/is-it-better-to-save-insert-the
    # -hashed-string-in-database-table-before-saving-th
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passw.encode(), salt)
    return hashed


def comparehash(u, passw):
    rows = lookupuser(u)
    if rows:
        if bcrypt.hashpw(passw.encode(), rows[0][1].encode()) == rows[0][1].encode():
            return True
        else:
            return False
    else:
        return False


def randomgen():
    while True:
        password = ''.join(
            secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(returnlen()))
        if checkpolicy(password):
            y = callhibp(password)
            if y == 0:
                break
    hashedpass = hashing(password)
    return hashedpass, password


def adduser(u, r, appid):
    hpass, passw = randomgen()
    result = insertuser(u, hpass, r, appid)
    if result:
        return True, passw
    else:
        return False, None


def updatepass(u):
    hpass, passw = randomgen()
    updatep(u, hpass)
    return passw


def lookupflag(u):
    rows = lookupuser(u)
    flag = rows[0][5]
    return flag
