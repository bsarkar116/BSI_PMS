# referenced password_strength module from https://pypi.org/project/password-strength/
from password_strength import PasswordPolicy as pp
from database import update_status, query_all
from datetime import datetime
import json

# Constant
time_format = "%Y-%m-%d %H:%M:%S"


def gen_policy(a, b, c, d, e, f):
    poli = {'Length': a, 'Upper': b, 'Lower': c, 'Digits': d, 'Special': e, 'Age': f,
            'Date': datetime.today().strftime(time_format)}
    with open('policy.json', "w", encoding="utf8") as outfile:
        json.dump(poli, outfile)
    pass_retention()


def load_policy():
    try:
        with open('policy.json') as json_file:
            pol = json.load(json_file)
        return pol
    except:
        print("Missing config file")


def return_len():
    pol = load_policy()
    return pol['Length']


def check_policy(p):
    pol = load_policy()
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

def pass_retention():
    flag = False
    pol = load_policy()
    rows = query_all()
    for i in range(len(rows)):
        current = datetime.today().strftime(time_format)
        age = datetime.strptime(current, time_format) - rows[i][3]
        delta = datetime.strptime(pol['Date'], time_format) - rows[i][3]
        if int(delta.total_seconds()) > 0 or int(age.days) > pol['Age']:
            update_status(rows[i][0])
            flag = True
    return flag
