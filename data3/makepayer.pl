#!/usr/bin/perl
# 
# makepayer.pl for Clique3
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

my $userid = $ARGV[0];
my $globalId = $ARGV[1];

print "userid = $userid\nglobalId = $globalId\n";

open JG, "< jg.key" or die "can't open jg.key\n";
$txt = join '', <JG> ;
chomp($txt);

print "txt = $txt\n";
my $cmd = qq{
cp payertemp.cpp payer$userid.cpp
};
system($cmd);
$cmd = qq{ perl -p -i.t -e 's/KEY/\Q$txt\E/mg' payer$userid.cpp
};

system($cmd);
$cmd = qq/g++ bn40.cpp payer$userid.cpp -o payer$userid/;
system($cmd);

# make the step1v2
open STEP1, "< d.key" or die "can't open d.key\n";
$step1 = join '', <STEP1>;
chomp($step1);
$cmd = qq{cp step1v2.cpp step1$userid.cpp};
system($cmd);
$cmd = qq{perl -p -i.t -e  's/STEP1KEY/\Q$step1\E/mg' step1$userid.cpp};
system($cmd);
$cmd = qq{g++ bn40.cpp step1$userid.cpp -o step1$userid};
system($cmd);
# endof make step1v2
$cmd =  "cp clienttemp2.py payer$userid.py; chmod 777 payer$userid.py";
system($cmd);
$cmd = "perl -p -i.t -e 's/USERID/$userid/mg' payer$userid.py";
system($cmd);
# import.py
system("/usr/bin/python3 import2cass.py $userid $globalId ");
# end of import.py
$cmd = "rm payer$userid.cpp payer$userid.cpp.t step1$userid.cpp.t step1$userid.cpp payer$userid.py.t jg.key d.key e.key";
system($cmd);
