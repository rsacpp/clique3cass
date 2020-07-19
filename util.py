#!/usr/bin/python3

#
# util.py for Clique3
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

import hashlib
import json


def path(alias):
    m = hashlib.sha256()
    m.update(alias.encode('utf-8'))
    dig = m.hexdigest()
    return '{0}'.format(dig[0])


def conf():
    f = open('conf', 'r')
    txt = ''
    while True:
        en = f.readline()
        en = en.strip()
        if en == '':
            break
        txt += en
    f.close()
    vals = json.loads(txt)
    return vals
