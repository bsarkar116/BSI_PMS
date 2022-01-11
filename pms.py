import string
import secrets
import hashlib
import requests
import pandas as pd
import policy as pol
import dbpersistance as db


def callhibp(p):
    flag = 0
    m = hashlib.sha1(p.encode('utf8')).hexdigest()
    query = "https://api.pwnedpasswords.com/range/" + m[:5]
    response = requests.get(query)
    for line in response.text.splitlines():
        a, b = line.split(":", 1)
        if m[5:] == a.lower():
            flag = 1
            break
    return flag


def ranpassgen(u):
    while True:
        password = ''.join(
            secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in
            range(pol.returnlen()))
        x = pol.checkpolicy(password)
        if x == 1:
            y = callhibp(password)
            if y == 0:
                break
    db.insertuser(u, password)


# def disppass(u):


def frontend():
    n = input("How many passwords are to be generated(one or batch): ")
    if n.lower() == "batch" or n.lower() == "m":
        df = pd.read_csv("users_batch.csv")
        for i in range(len(df)):
            user = df.iloc[i, 0]
            ranpassgen(user)
            # disppass(user)
        print('Password batch generated and stored.')
    elif n.lower() == "one" or n == '1':
        user = input("Please provide username: ")
        ranpassgen(user)
        # disppass(user)
    else:
        print("Please enter a valid option between one or batch")


frontend()
