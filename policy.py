import json
from password_strength import PasswordPolicy as pp  #
from database import updatestatus, queryall
from datetime import datetime


def genpolicy(a, b, c, d, e, f):
    poli = {'Length': a, 'Upper': b, 'Lower': c, 'Digits': d, 'Special': e, 'Age': f,
            'Date': datetime.today().strftime("%Y-%m-%d %H:%M:%S")}
    with open('policy.json', "w", encoding="utf8") as outfile:
        json.dump(poli, outfile)
    passretention()


def loadpolicy():
    try:
        with open('policy.json') as json_file:
            pol = json.load(json_file)
        return pol
    except FileNotFoundError:
        print("Missing config file")


def returnlen():
    pol = loadpolicy()
    return pol['Length']


def checkpolicy(p):
    pol = loadpolicy()
    policy = pp.from_names(
        length=pol['Length'],  # min length
        uppercase=pol['Upper'],  # min no. uppercase letters
        nonletters=pol['Lower'],  # min no. any other characters
        numbers=pol['Digits'],  # min no. digits
        special=pol['Special'],  # min no. special characters
    )
    if not policy.test(p):
        return True
    else:
        return False


# total_seconds() referenced from https://docs.python.org/3.9/library/datetime.html#datetime.timedelta

def passretention():
    flag = False
    pol = loadpolicy()
    rows = queryall()
    for i in range(len(rows)):
        current = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        age = datetime.strptime(current, "%Y-%m-%d %H:%M:%S") - rows[i][3]
        delta = datetime.strptime(pol['Date'], "%Y-%m-%d %H:%M:%S") - rows[i][3]
        if int(delta.total_seconds()) > 0:
            updatestatus(rows[i][0])
            flag = True
        elif int(age.days) > pol['Age']:
            updatestatus(rows[i][0])
            flag = True
    return flag
