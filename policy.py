import json
from password_strength import PasswordPolicy as pp

with open('policy.json') as json_file:
    pol = json.load(json_file)


def genpolicy():
    a, b, c, d, e, f = input('Enter password policy in following order -> length, Number of Upper case chars, '
                             'Number of Lower case chars, Number of digits, Number of special chars, Password '
                             'retention duration: '
                             '').split(',')
    poli = {'Length': a, 'Upper': b, 'Lower': c, 'Digits': d, 'Special': e, 'Age': f}
    with open('policy.json', "w", encoding="utf8") as outfile:
        json.dump(poli, outfile)


def returnlen():
    return int(pol['Length'])


def checkpolicy(p):
    flag = 0
    policy = pp.from_names(
        length=int(pol['Length']),  # min length
        uppercase=int(pol['Upper']),  # min no. uppercase letters
        nonletters=int(pol['Lower']),  # min no. any other characters
        numbers=int(pol['Digits']),  # min no. digits
        special=int(pol['Special']),  # min no. special characters
    )
    if not policy.test(p):
        flag = 1
    return flag
