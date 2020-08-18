#!/usr/bin/perl
my $userid = $ARGV[0];
my $globalId = $ARGV[1];

print "userid = $userid\nglobalId = $globalId\n";

open JG, "< jg.key" or die "can't open jg.key\n";
$txt = join '', <JG> ;
chomp($txt);

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

# import.py
system("/usr/bin/python3 import2cass.py $userid $globalId ");
# end of import.py
$cmd = "rm payer3$userid.cpp payer3$userid.cpp.t step1$userid.cpp.t step1$userid.cpp jg.key d.key e.key";
system($cmd);
