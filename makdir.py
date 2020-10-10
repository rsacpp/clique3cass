from sys import argv
for a in range(0, 256):
    print('mkdir {}/{:02x}'.format(argv[1], a))
