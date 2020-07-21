#!/usr/bin/perl
#use Data::Dumper;
# 
# parseoutput.pl for Clique3
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


my $str;
foreach(<>){
    if (m/INTEGER/){
	s/.*(:\w+)\s*$/$1/;
	$str.=$_;
    }
}

my @ar = split /:/,$str;
my $pq =  scalar reverse $ar[2];
open D, '>', 'd.key' or die "cannot open d.key\n";
print D lc($pq).'@@'. lc(scalar reverse $ar[4]);
print D "\n";
close D;

open JG, '>', 'jg.key' or die "cannot open jg.key\n";
print JG lc($pq).'@@'.lc(scalar reverse $ar[9]);
print JG "\n";
close JG;

open E, '>', 'e.key' or die "cannot open e.key\n";
print E lc($pq).'@@'.lc(scalar reverse $ar[3]);
print E "\n";
close E;
