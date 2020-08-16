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

print "txt = $txt\n";
my $cmd = qq{
cp issuertemp.cpp issuer$symbol.cpp
};
system($cmd);

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

$cmd =  "cp issuertemp2kafka.py issuer$symbol.py; chmod 777 issuer$symbol.py";
system($cmd);
$cmd = "perl -p -i.t -e 's/SYMBOL/$symbol/mg' issuer$symbol.py";
system($cmd);

system("/usr/bin/python3 importissuer2cass.py $userid $symbol $globalId");

$cmd = "rm issuer3$symbol.cpp issuer3$symbol.cpp.t issuer$symbol.cpp issuer$symbol.cpp.t issuer$symbol.py.t jg.key d.key e.key step1$symbol.cpp step1$symbol.cpp.t";
system($cmd);
