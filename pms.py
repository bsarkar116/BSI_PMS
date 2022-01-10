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
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user=usr,
    password=passw,
    database=db
)

with open('policy.json') as json_file:
    pol = json.load(json_file)


def passpoli():
    a, b, c, d, e, f = input('Enter password policy in following order -> length, Number of Upper case chars, '
                             'Number of Lower case chars, Number of digits, Number of special chars, Password '
                             'retention duration: '
                             '').split(',')
    poli = {'Length': a, 'Upper': b, 'Lower': c, 'Digits': d, 'Special': e, 'Age': f}
    with open('policy.json', "w", encoding="utf8") as outfile:
        json.dump(poli, outfile)


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


def checkpoli(p):
    length = int(pol['Length'])
    flag = 0
    policy = pp.from_names(
        length=length,  # min length
        uppercase=int(pol['Upper']),  # min no. uppercase letters
        nonletters=int(pol['Lower']),  # min no. any other characters
        numbers=int(pol['Digits']),  # min no. digits
        special=int(pol['Special']),  # min no. special characters
    )
    if not policy.test(p):
        flag = 1
    return flag


def ranpassgen(u):
    length = int(pol['Length'])
    while True:
        password = ''.join(
            secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in
            range(length))
        x = checkpoli(password)
        if x == 1:
            y = callhibp(password)
            if y == 0:
                break
    mycursor = mydb.cursor()
    query = "INSERT INTO users (user, pass) VALUES (%s, %s)"
    mycursor.execute(query, (u, password))
    mydb.commit()


# def disppass:

def frontend():
    n = input("How many passwords are to be generated(one or batch): ")
    if n.lower() == "batch" or n.lower() == "m":
        df = pd.read_csv("users_batch.csv")
        for i in range(len(df)):
            user = df.iloc[i, 0]
            ranpassgen(user)
        print('Password batch generated and stored.')
    elif n.lower() == "one" or n == '1':
        user = input("Please provide username: ")
        ranpassgen(user)
        print('Password generated and stored')
    else:
        print("Please enter a valid option between one or batch")


# frontend()
