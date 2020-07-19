#!/usr/bin/python3
#
# processIssue.py for Clique3
# Copyright (C) 2018, Gu Jun
#
# This file is part of Clique3.
# Clique3 is  free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

# Clique3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Clique3. If not, see <http://www.gnu.org/licenses/>.

import sys
import hashlib
import random
import psycopg2
from subprocess import Popen
sys.path.append('/path/to/util.py')
import util

dbConnectStr = util.conf().get('pgConn3')

symbol = sys.argv[1]
quantity = sys.argv[2]
globalId = sys.argv[3]
print("symbol={0} quantity={1}".format(symbol, quantity))

# first get the id of the note, take a random number
sha256 = hashlib.sha256()
sha256.update("{0}".format(symbol).encode('utf-8'))
sha256.update("{0}".format(random.random()).encode('utf-8'))
sha256.update("{0}".format(quantity).encode('utf-8'))

digest = sha256.hexdigest()
length = len(digest)
noteId = digest[length-8:]

# need to check whether the symbol+noteId is global unique

conn = psycopg2.connect(dbConnectStr)
cur = conn.cursor()


try:
    while True:
        cur.execute("""
        select count(*) from ownership0 where symbol=%s and "noteId"=%s and clique = '3'
        """, [symbol, noteId])
        count = cur.fetchone()[0]
        conn.commit()
        if count == 0:
            break
        # if an existing entry found, generate another id
        sha256.update("{0}".format(random.random()).encode('utf-8'))
        digest = sha256.hexdigest()
        length = len(digest)
        noteId = digest[length-8:]
        print("count={0}".format(count))
except psycopg2.Error as err:
    print("SQLError {0}".format(err))
finally:
    cur.close()
    conn.close()

text = "||{0}||{1}->".format(noteId, quantity)

pro3 = Popen(['/usr/bin/python3', '/{0}/{1}/issuer{2}.py'.format(util.conf().get('playerepo3'), util.path(symbol), symbol), text, globalId], stdin=None, stdout=None)
pro3.wait()
