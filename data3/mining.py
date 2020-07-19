#!/usr/bin/python3
import random
import hashlib
import sys
from subprocess import Popen, PIPE
from datetime import datetime

raw = sys.argv[1]
print("raw = {0}".format(raw))

sha1 = hashlib.sha1()
while True:
    sha1.update('{0}'.format(random.random()).encode('utf-8'))
    code = sha1.hexdigest()
    print("{1}: code = {0}".format(code, datetime.now()))
    pro0 = Popen(['./mining', raw, code], stdin=None, stdout=PIPE)
    res = pro0.communicate()[0].decode().strip()
    if res.startswith('^^fff'):
        print("res = {0}".format(res))
        break
