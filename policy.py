import json
from password_strength import PasswordPolicy as pp  #
from database import lookup
from datetime import date


def genpolicy():
    a, b, c, d, e, f = input('Enter password policy in following order -> length, Number of Upper case chars, '
                             'Number of Lower case chars, Number of digits, Number of special chars, Password '
                             'retention duration: '
                             '').split(',')
    poli = {'Length': a, 'Upper': b, 'Lower': c, 'Digits': d, 'Special': e, 'Age': f}
    with open('policy.json', "w", encoding="utf8") as outfile:
        json.dump(poli, outfile)


try:
    with open('policy.json') as json_file:
        pol = json.load(json_file)
except FileNotFoundError:
    print("Policy file not found. Please generate one first")


def returnlen():
    return int(pol['Length'])


def checkpolicy(p):
    policy = pp.from_names(
        length=int(pol['Length']),  # min length
        uppercase=int(pol['Upper']),  # min no. uppercase letters
        nonletters=int(pol['Lower']),  # min no. any other characters
        numbers=int(pol['Digits']),  # min no. digits
        special=int(pol['Special']),  # min no. special characters
    )
    if not policy.test(p):
        return True
    else:
        return False


def passretention(u, passw):
    rows = lookup(u)
    days = date.today() - rows[0][3]
    if checkpolicy(passw) and int(days) <= int(pol['Age']):
        return False
    else:
        return True
