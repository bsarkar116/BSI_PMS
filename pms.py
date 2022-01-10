import string
import secrets
import json
import hashlib
import requests
import mysql.connector
import pandas as pd
from password_strength import PasswordPolicy as pp

with open('dbcreds.json') as db_file:
    data = json.load(db_file)
usr = str(data["User"])
passw = str(data["Password"])
db = str(data["Database"])


def passpoli():
    a, b, c, d, e, f = input('Enter password policy in following order -> length, Number of Upper case chars, '
                             'Number of Lower case chars, Number of digits, Number of special chars, Password '
                             'retention duration: '
                             '').split(',')
    pol = {'Length': a, 'Upper': b, 'Lower': c, 'Digits': d, 'Special': e, 'Age': f}
    with open('policy.json', "w", encoding="utf8") as outfile:
        json.dump(pol, outfile)


# def disppass:

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
    if flag == 1:
        return 1
    else:
        return 0


def ranpassgen(u):
    with open('policy.json') as json_file:
        pol = json.load(json_file)
    length = int(pol['Length'])
    policy = pp.from_names(
        length=length,  # min length
        uppercase=int(pol['Upper']),  # min no. uppercase letters
        nonletters=int(pol['Lower']),  # min no. any other characters
        numbers=int(pol['Digits']),  # min no. digits
        special=int(pol['Special']),  # min no. special characters
    )
    while True:
        password = ''.join(
            secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in
            range(length))
        if not policy.test(password):
            x = callhibp(password)
            if x == 0:
                break
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user=usr,
        password=passw,
        database=db
    )
    mycursor = mydb.cursor()
    query = "INSERT INTO users (user, Name) VALUES(?, ?)", (u, password)
    mycursor.execute(query)


def frontend():
    n = input("How many passwords are to be generated(one or batch): ")
    if n.lower() == "batch":
        df = pd.read_csv("users_batch.csv")
        for i in range(len(df)):
            user = df.iloc[i, 0]
            ranpassgen(user)
        print('Password batch generated and stored.')
    elif n.lower() == "one":
        user = input("Please provide username: ")
        ranpassgen(user)
        print('Password generated.')
    else:
        print("Please enter a valid option between one or batch")
