import string
import secrets
import hashlib
import requests
import bcrypt
import pandas as pd
from validations import validate_csv
from policy import check_policy, return_len
from database import insert_user, lookup_user, updatep, del_user


def call_hibp(p):
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


# referenced from https://stackoverflow.com/questions/8870190/is-it-better-to-save-insert-the
# -hashed-string-in-database-table-before-saving-th

def compare_hash(u, passw):
    rows = lookup_user(u)
    if rows:
        if bcrypt.hashpw(passw.encode(), rows[0][1].encode()) == rows[0][1].encode():
            return True
        else:
            return False
    else:
        return False


def random_gen():
    exclude = {"'", '"'}
    puncts = ''.join(ch for ch in string.punctuation if ch not in exclude)
    while True:
        password = ''.join(
            secrets.choice(string.ascii_letters + string.digits + puncts) for i in range(return_len()))
        if check_policy(password):
            y = call_hibp(password)
            if y == 0:
                break
    salt = bcrypt.gensalt()
    hashedpass = bcrypt.hashpw(password.encode(), salt)
    return hashedpass, password


def adduser(u, r, appid):
    hpass, passw = random_gen()
    result = insert_user(u, hpass, r, appid)
    if result:
        return True, passw
    else:
        return False, None


def batch_add(file):
    df = pd.read_csv(file)
    templist = []
    if validate_csv(df):
        df_new = df.drop(["Role", "AppID"], axis=1)
        for i in range(len(df)):
            result, passw = adduser(df.iloc[i, 0], df.iloc[i, 1], df.iloc[i, 2])
            if result:
                templist.append(passw)
            else:
                templist.append("Duplicate user")
        df_new["Password"] = templist
        return df_new
    else:
        df = pd.DataFrame()
        return df


def batch_remove(file):
    df = pd.read_csv(file)
    templist = []
    if validate_csv(df):
        df = df[["User"]]
        for i in range(len(df)):
            result = del_user(df.iloc[i, 0])
            if result:
                templist.append("User removed")
            else:
                templist.append("User not found")
        df["Status"] = templist
        return df
    else:
        df = pd.DataFrame()
        return df


def update_pass(u):
    hpass, passw = random_gen()
    updatep(u, hpass)
    return passw