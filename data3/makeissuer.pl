#!/usr/bin/perl
my $userid = $ARGV[0];
my $symbol = $ARGV[1];
my $globalId = $ARGV[2];

my $userCode = unpack("H*", $userid);
my $symbolCode = unpack("H*", $symbol);

print "userid = $userid\nuserCode = $userCode\nsymbol = $symbol\nsymbolCode = $symbolCode\n";

open JG, "< jg.key" or die "can't open jg.key\n";
$txt = join '', <JG> ;
chomp($txt);

#standalone part
$cmd = qq{cp issuertemp3.cpp issuer3$symbol.cpp
};
system($cmd);

$cmd = qq{
perl -p -i.t -e 's/KEY/\Q$txt\E/mg' issuer3$symbol.cpp
};
system($cmd);

$cmd = qq{
perl -p -i.t -e 's/SYMBOL/\Q$symbol\E/mg' issuer3$symbol.cpp
};
system($cmd);

$cmd = qq{
perl -p -i.t -e 's/ALIAS/\Q$userid\E/mg' issuer3$symbol.cpp
};
system($cmd);

$cmd = qq{
g++ bn40.cpp issuer3$symbol.cpp -lboost_system -lpthread -o issuer3$symbol
};
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

system("/usr/bin/python3 importissuer2cass.py $userid $symbol $globalId");

$cmd = "rm issuer3$symbol.cpp issuer3$symbol.cpp.t jg.key d.key e.key step1$symbol.cpp step1$symbol.cpp.t";
system($cmd);
