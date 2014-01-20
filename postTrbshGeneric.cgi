#!/opt/app/d1fnc1c1/perl/bin/perl -w
# 
# postTrbshGeneric.cgi should be used as the generic post script that is invoked upon Submit from your node-specific uiTrbsh page.
# To use it, insert the following hidden fields into your uiTrbsh script:
#
#	<input type='hidden' name='node_type_ID' value='n'>
# 		- 'n' is your Node Type ID.
#
#	<input type='hidden' name='node_type_txt' value='n'>
# 		- 'n' is the label for the message emitted while waiting for your node to respond.
#
#	<input type='hidden' name='my_UI' value='/cgi-bin/uiTrbshN.cgi'>
# 		- This is the relative path to your uiTrbsh script, for hyper-linking the header.
#
# And then find your invocation to doPrintTrbshHeading and change it to this:
#
# doPrintTrbshHeading("Generic", "n");
# 	- 'n' will show up in your heading, prepended to 'Troubleshooting'
#
# Also, in order to correctly map the GUI elements in your uiTrbsh page to the cgi_data hash table in this file, you must
# assign the 'name' HTML property to specific values:
#
#	- 'Action/Command' selection box should be named ACTIONTYPENUM
#	- 'Host Name' selection box should be named NODEID
#
# Include Trbsh library.

use strict;
use warnings;

use libs::libConfigN;
use libs::libUtilsN;
use libs::libFileUtilsN;
require 'libs/libTrbshN.pl';

# declare global variables
our $DEBUG = 0;
our $node_type_ID = "";
our $node_type_txt = "";
our $my_UI = "";
our $ELEATROOT = libConfig::getEleatCfgVal('ELEATROOT');		# define at outset - used in Log & Debug functions

my %cgi_data;

our ($onMark, $offMark, $optMark);
our $command = "";
our $sulog = 0;		# FIXME: used as arg to doCleanupPost() but never set??

main();
exit 0;

# initiate
# returns 1 on success; 0 on failure
sub initiate {
	libUtils::DBG_PRINT(33, "Enter sub initiate", @_);
	my @commands = ();

	if (defined($cgi_data{'DEBUG'})) {
		$DEBUG = $cgi_data{'DEBUG'};
	}

	my ($trbsh_tmp, $trbsh_log, $trbsh_data) = doSetLogs($node_type_ID, $cgi_data{'NODEID'});
	if ($trbsh_tmp eq "" || $trbsh_log eq "" || $trbsh_data eq "") {
		libUtils::DBG_PRINT(33, "Exit sub initiate");
		return 0;
	}
	push @commands, "LOGFILE=$trbsh_log";
	push @commands, "TEMPFILE=$trbsh_tmp";
	push @commands, "DATAFILE=$trbsh_data";
	$command = join " ", @commands;

	libUtils::DBG_PRINT(33, "Exit sub initiate");
	return 1;
} # end initiate()

# proc_N()
sub proc_N {
	libUtils::DBG_PRINT(33, "Enter sub proc_N	", @_);
	# Preparation for trouble shooting
	doPreparePost($cgi_data{'NODEID'});

	my $my_script = libConfig::getExecByNode($cgi_data{'NODEID'});

	DBG_PRINT2("<B>($my_script parms)</B> -- $command<br><b>--end parms</b>");

	my $status = buildDataFile(%cgi_data);
	if ($status ne "") {
		libUtils::PERROR("buildDataFile failed with $status");
	} else {
		# Call N.pl to do the troubleshooting
		libUtils::DBG_PRINT(10, "executing ${ELEATROOT}/$my_script $command");
		$status = forkExec("${ELEATROOT}/$my_script $command", 1, 0);
		if ($status ne "") {
			print "STATUS=$status<br>\n";
		}
		# Print the log lists
		doPrintLogsList();
	}

	# Cleanup
	doCleanupPost("N", $sulog);
	libUtils::DBG_PRINT(33, "Exit sub proc_N	");
} # end proc_N()

#
# Write line to DEBUG file (if $DEBUG >=1 )
#
sub DBG_PRINT2 {
	my ($parm) = @_;
	if ($DEBUG >= 1) {
		$parm =~ tr/\r//;
		$parm =~ tr/\n//;
		chomp(my $time = `date "+%H:%M:%S"`);
		print "<b>** postDBG * $time **</b> ", $parm, ":;<br>\n";		# FIXME: postDBG handle not defined!
	}
} # end DBG_PRINT2()

#
# main()
#
sub main {
	$| = 1;  # turn off buffering
	libFileUtils::logUserAction();
	%cgi_data = libUtils::getHTTPVars();

	$node_type_txt = $cgi_data{'node_type_txt'};
	$node_type_ID = $cgi_data{'node_type_ID'};
	$my_UI = $cgi_data{'my_UI'};

	print "Content-type: text/html \n\n";

	libUtils::DBG_PRINT(10, "main - call logUserAction()");

	libUtils::DBG_PRINT(10, "main - call doPrintHTMLHeadPost()");

	doPrintHTMLHeadPost("$node_type_txt Troubleshooting", $my_UI);

	libUtils::DBG_PRINT(10, "main - call initiate()");

	if (initiate() == 1) {
		libUtils::DBG_PRINT(10, "main - call proc_N	()");
		proc_N();
	} else {
		libUtils::PERROR("main - initiate() failed");
		doPrintExceptions();
	}
	libUtils::DBG_PRINT(10, "main - call doPrintHTMLTailPost()");
	doPrintHTMLTailPost();
} # end main()
