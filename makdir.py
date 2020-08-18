from sys import argv
import os
aa = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

for a in aa:
    for b in aa:
        cmd = 'mkdir {0}/{1}{2}'.format(argv[1], a, b)
        print(cmd)
        os.popen(cmd)


