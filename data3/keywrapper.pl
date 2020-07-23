#!/usr/bin/perl
# 
# keywrapper.pl for Clique3
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

#!/usr/bin/perl
my $dir = $ARGV[0];
my $bits = $ARGV[1];
print("dir=$dir,bits=$bits\n");
my $cmd = qq%$dir/openssl-1.0.2o/apps/openssl genrsa $bits|$dir/openssl-1.0.2o/apps/openssl asn1parse|/usr/bin/perl parseoutput.pl
    %;
print("$cmd\n");
system($cmd);
