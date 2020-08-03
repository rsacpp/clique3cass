#!/usr/bin/python3

# reserved0.py for Clique3
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

ar = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
counter = -10

for c in ar:
    text = '{0}{0}{0}{0}'.format(c)
    for c2 in ar:
        print("insert into reserved0(seq, word)values({0},'{1}');".format(counter, '{0}{1}'.format(c2,text)))
        counter -= 1
        print("insert into reserved0(seq, word)values({0},'{1}');".format(counter, '{0}{1}'.format(text,c2)))
        counter -= 1
