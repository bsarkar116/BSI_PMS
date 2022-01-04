import string
import secrets
import json
import requests
from password_strength import PasswordPolicy


def passpoli():
    a, b, c, d, e, f = input('Enter password policy in following order -> length, Number of Upper case chars, '
                             'Number of Lower case chars, Number of special chars, Password retention duration: '
                             '').split(',')
    data = {'Length': a, 'Upper': b, 'Lower': c, 'Digits': d, 'Special': e, 'Age': f}
    with open('policy.json', "w", encoding="utf8") as outfile:
        json.dump(data, outfile)

# def disppass:


def ranpassgen(n):
    with open('policy.json') as json_file:
        data = json.load(json_file)
    length = int(data['Length'])
    policy = PasswordPolicy.from_names(
        length=length,  # min length
        uppercase=int(data['Upper']),  # min no. uppercase letters
        nonletters=int(data['Lower']),  # min no. any other characters
        numbers=int(data['Digits']),  # min no. digits
        special=int(data['Special']),  # min no. special characters
    )
    if n > 1:
        while n > 0:
            password = ''.join(
                secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in
                range(length))
            if policy.test(password):
                break
            n = n - 1
    else:
        while True:
            password = ''.join(
                secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in
                range(length))
            if policy.test(password):
                break

    return str(password)
