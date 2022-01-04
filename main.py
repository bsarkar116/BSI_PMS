# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pms

# pms.passpoli()

print("How many passwords are to be generated")
n = int(input())
if n > 1:
    print('Password generated: ' + pms.ranpassgen(n))
else:
    print('Password generated: ' + pms.ranpassgen(n))
