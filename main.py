# This is the main python script

import pms

# pms.passpoli()

n = input("How many passwords are to be generated: ")
n = int(n)
if n > 1:
    print('Password batch generated and stored: ')
else:
    print('Password generated: ' + pms.ranpassgen(n))
    # pms.ranpassgen(n)
