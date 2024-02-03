from password_strength import PasswordPolicy as pp
from database import update_status, query_acc, lookup_status
from datetime import datetime
from validations import validate_json
from schema import policySchema
import json
import os

# DV7, AH23
time_format = "%Y-%m-%d %H:%M:%S"


def read_pol():
    with open(r"C:\Users\BrijitSarkar\Desktop\pms\policy\policy.json", 'r', encoding='utf-8') as file:
        p = json.load(file)
    return p


def del_temp():
    if os.path.exists(r"C:\Users\BrijitSarkar\Desktop\pms\temp\temp_policy.json"):
        os.remove(r"C:\Users\BrijitSarkar\Desktop\pms\temp\temp_policy.json")


def gen_policy(a, b, c, d, e, f):
    s = int(b) + int(c) + int(d) + int(e)
    if a >= s:
        poli = {"Length": a, "Upper": b, "Lower": c, "Digits": d, "Special": e, "Age": f,
                "Date": str(datetime.today().strftime(time_format))}
        with open(r"C:\Users\BrijitSarkar\Desktop\pms\policy\policy.json", 'w', encoding='utf-8') as fi:
            json.dump(poli, fi)
        pass_retention()
        return True
    else:
        return False


def add_pol():
 try:
    with open(r"C:\Users\BrijitSarkar\Desktop\pms\temp\temp_policy.json", 'r', encoding='utf-8') as file:
        temp_pol = json.load(file)
        isvalid = validate_json(temp_pol, policySchema)
        if isvalid:
            resp = gen_policy(temp_pol["Length"], temp_pol["Upper"], temp_pol["Lower"], temp_pol["Digits"],
                              temp_pol["Special"], temp_pol["Age"])
            if resp:
                del_temp()
                return True
            else:
                del_temp()
                return False
        else:
            del_temp()
            return False
 except json.decoder.JSONDecodeError as e:
     del_temp()
     return False


def check_policy(pa):
    pol = read_pol()
    policy = pp.from_names(
        length=pol['Length'],  # Length
        uppercase=pol['Upper'],  # min no. uppercase letters
        nonletters=pol['Lower'],  # min no. any other characters
        numbers=pol['Digits'],  # min no. digits
        special=pol['Special'],  # min no. special characters
    )
    if not policy.test(pa):
        return True
    else:
        return False


def pass_retention():
    flag = False
    rows, c = query_acc(None, 1)
    pol = read_pol()
    for i in range(len(rows)):
        current = datetime.today().strftime(time_format)
        age = datetime.strptime(current, time_format) - rows[i][8]
        delta = datetime.strptime(pol['Date'], time_format) - rows[i][8]
        if int(delta.total_seconds()) > 0 or int(age.days) > int(pol['Age']):
            update_status(rows[i][10])
            flag = True
    return flag


def check_status(ID):
    rows = lookup_status(ID)
    if rows:
        return True
    else:
        return False
