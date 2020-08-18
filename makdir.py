from sys import argv
import os
import string
h = string.hexdigits.lower()

for i in range(0, 16):
    a = h[i:i+1]
    for j in range(0, 16):
        #print('i= {0}, j = {1}'.format(i ,j))
        b = h[j: j+1]
        cmd = 'mkdir {0}/{1}{2}'.format(argv[1], a, b)
        print(cmd)
        os.popen(cmd)


