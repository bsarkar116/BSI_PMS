import string
import secrets
import json
import hashlib
import requests
import crypt
from password_strength import PasswordPolicy


def passpoli():
    a, b, c, d, e, f = input('Enter password policy in following order -> length, Number of Upper case chars, '
                             'Number of Lower case chars, Number of digits, Number of special chars, Password '
                             'retention duration: '
                             '').split(',')
    data = {'Length': a, 'Upper': b, 'Lower': c, 'Digits': d, 'Special': e, 'Age': f}
    with open('policy.json', "w", encoding="utf8") as outfile:
        json.dump(data, outfile)
    encryptor = crypt.Secure()
    mykey = encryptor.key_create()
    encryptor.key_write(mykey, 'mykey.key')
    loaded_key = encryptor.key_load('mykey.key')
    encryptor.file_encrypt(loaded_key, 'policy.json')


pass


# def disppass:

def callhibp(passw):
    flag = 0
    m = hashlib.sha1(passw.encode('utf8')).hexdigest()
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


pass


def ranpassgen(n):
    encryptor = crypt.Secure()
    loaded_key = encryptor.key_load('mykey.key')
    encryptor.file_decrypt(loaded_key, 'policy.json')
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
        for i in range(n):
            while True:
                password = ''.join(
                    secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in
                    range(length))
                if not policy.test(password):
                    x = callhibp(password)
                    if x == 0:
                        break
    else:
        while True:
            password = ''.join(
                secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in
                range(length))
            if not policy.test(password):
                x = callhibp(password)
                if x == 0:
                    break
    encryptor = crypt.Secure()
    mykey = encryptor.key_create()
    encryptor.key_write(mykey, 'mykey.key')
    loaded_key = encryptor.key_load('mykey.key')
    encryptor.file_encrypt(loaded_key, 'policy.json')
    return str(password)


pass
