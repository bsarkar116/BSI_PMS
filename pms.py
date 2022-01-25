import string
import secrets
import hashlib
import requests
from policy import checkpolicy, returnlen
from database import insertuser


def callhibp(p):
    flag = 0
    m = hashlib.sha1(p.encode('utf8')).hexdigest()
    query = "https://api.pwnedpasswords.com/range/" + m[:5]
    response = requests.get(query)
    for line in response.text.splitlines():  #
        a, b = line.split(":", 1)
        if m[5:] == a.lower():
            flag = 1
            break
    return flag


def ranpassgen(u, r):
    while True:
        password = ''.join(
            secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(returnlen()))
        if checkpolicy(password):
            y = callhibp(password)
            if y == 0:
                break
    result = insertuser(u, password, r)
    if result:
        return True
    else:
        return False
