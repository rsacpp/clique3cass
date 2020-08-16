#!/usr/bin/perl
my $userid = $ARGV[0];
my $globalId = $ARGV[1];

print "userid = $userid\nglobalId = $globalId\n";

open JG, "< jg.key" or die "can't open jg.key\n";
$txt = join '', <JG> ;
chomp($txt);

my $cmd = qq{
cp payertemp.cpp payer$userid.cpp
};
system($cmd);
$cmd = qq{ perl -p -i.t -e 's/KEY/\Q$txt\E/mg' payer$userid.cpp
};
system($cmd);

$cmd = qq/g++ bn40.cpp payer$userid.cpp -o payer$userid/;
system($cmd);

$cmd = qq{cp payertemp3.cpp payer3$userid.cpp};
system($cmd);

$cmd = qq{
perl -p -i.t -e 's/KEY/\Q$txt\E/mg' payer3$userid.cpp
};
system($cmd);

$cmd = qq{
g++ bn40.cpp payer3$userid.cpp -lboost_system -lpthread -o payer3$userid
};
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
$cmd =  "cp clienttemp3.py payer$userid.py; chmod 777 payer$userid.py";
system($cmd);
$cmd = "perl -p -i.t -e 's/USERID/$userid/mg' payer$userid.py";
system($cmd);
# import.py
system("/usr/bin/python3 import2cass.py $userid $globalId ");
# end of import.py
$cmd = "rm payer$userid.cpp payer$userid.cpp.t step1$userid.cpp.t step1$userid.cpp payer$userid.py.t jg.key d.key e.key";
system($cmd);
