#!/usr/bin/perl
# 
# makeissuer.pl for Clique3
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

sub convert{
    my @tmp;
    my $str = $_[0];
    $i = 0;
    for(; $i < length($str); $i++){
        $ch = substr($str,$i, 1);
        $o = ord($ch);
        $j = 0;
        for(; $j < 2; $j++){
            $c =  sprintf("%x",($o>>(4*$j))&0xf);
	    push @tmp, $c;
        }
    }
    return join '', @tmp;
}

my $userid = $ARGV[0];
my $symbol = $ARGV[1];
my $globalId = $ARGV[2];

my $userCode = &convert($userid);
my $symbolCode = &convert($symbol);

print "userid = $userid\nuserCode = $userCode\nsymbol = $symbol\nsymbolCode = $symbolCode\n";

open JG, "< jg.key" or die "can't open jg.key\n";
$txt = join '', <JG> ;
chomp($txt);

print "txt = $txt\n";
my $cmd = qq{
cp issuertemp.cpp issuer$symbol.cpp
};
system($cmd);

$cmd = qq{ perl -p -i.t -e 's/KEY/\Q$txt\E/mg' issuer$symbol.cpp
};
system($cmd);

$cmd = qq{perl -p -i.t -e 's/SYMBOL/\Q$symbolCode\E/mg' issuer$symbol.cpp};
system($cmd);

$cmd = qq{perl -p -i.t -e 's/ALIAS/\Q$userCode\E/mg' issuer$symbol.cpp};
system($cmd);


$cmd = qq/g++ bn40.cpp issuer$symbol.cpp -o issuer$symbol/;
system($cmd);
#make step1v2
open STEP1, "< d.key" or die "can't open d.key\n";
$step1 = join '', <STEP1>;
chomp($step1);
$cmd = qq{cp step1v2.cpp step1$symbol.cpp};
system($cmd);
$cmd = qq{perl -p -i.t -e  's/STEP1KEY/\Q$step1\E/mg' step1$symbol.cpp};
system($cmd);
$cmd = qq{g++ bn40.cpp step1$symbol.cpp -o step1$symbol};
system($cmd);
#end of make step1v2

$cmd =  "cp issuertemp2.py issuer$symbol.py; chmod 777 issuer$symbol.py";
system($cmd);
$cmd = "perl -p -i.t -e 's/SYMBOL/$symbol/mg' issuer$symbol.py";
system($cmd);

system("/usr/bin/python3 importissuer2cass.py $userid $symbol $globalId");

$cmd = "rm issuer$symbol.cpp issuer$symbol.cpp.t issuer$symbol.py.t jg.key d.key e.key step1$symbol.cpp step1$symbol.cpp.t";
system($cmd);
