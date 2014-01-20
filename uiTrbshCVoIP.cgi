#!/opt/app/d1fnc1c1/perl/bin/perl -w

use strict;
use warnings;

use libs::libConfigN;
use libs::libFileUtilsN;
use libs::libWebUtils;
use libs::libAux;
require 'libs/libTrbshN.pl';

$| = 1;	#turn off buffering
libFileUtils::logUserAction();
print "Content-type: text/html \n\n";

# global variables
our $DEBUG = 0;
my $primary_node_type_ID = "Lucent_CVOIP";
my $secondary_node_type_ID = "SS8_CVOIP";
my %primary_node_cfg_hash;
my %secondary_node_cfg_hash;
my %cgi;
my $super_user;

# global variables to work around 'use strict' errors
our ($onMark, $offMark, $optMark);

our $ELEATROOT = libConfig::getEleatCfgVal("ELEATROOT");

our @yes_no = (
	["Y", "Yes"],
	["N", "No"]
);

our %fields = (
	'caseid' => [ "Case ID", &libAux::case_ID_note, "req", "text", "18", "18 character alphanumeric", "" ],
	'coid' => [ "COID", &libAux::COID_note, "req", "text", "16", "16 digits - either MDN + MUID or MIN + MUID", "" ],
	'serviceid' => [ "Service ID", &libAux::service_ID_note, "opt", "text", "16", "MDN + MUID", ""  ],
	'location' => [ "Mobile Locator", &libAux::location_note, "req", "select", \@yes_no, "Y", ""  ],
	'DDE' => [ "DDE Authorized", &libAux::DDE_note, "req", "select", \@yes_no, "N", ""  ],
	'SMS' => [ "SMS Type", &libAux::SMS_note, "req", "select", [["N", "None"], ["messages", "Messages"], ["messages+content","Messages + Content"]], "N", ""  ],
	'SURVTYPE' => [ "Surveillance Type", "Surveillance Type expl", "req", "select", [["ALL", "All"], ["DATA", "Call Data"], ["CONTENT", "Call Content"]], "DATA", ""  ],
	'services' => [ "Service Type", "Service Type expl", "req", "select", [["IMSI", "IMSI"], ["MSISDN", "MSISDN"], ["IMEI", "IMEI"], ["EMAIL", "E-mail"], ["LOGIN", "Login"], ["IP4", "IPv4"], ["IP6", "IPv6"], ["DHCPMAC", "DHCP-MAC"], ["DHCPOPT82", "DHCP-OPT82"], ["TRUNKCLLI", "TRUNK_CLLI"]], "IMSI", ""  ],
	'judge' => ["Judge", &libAux::judge_note, "opt", "text", "24", "string up to length 24", ""  ],
	'region' => ["Region", &libAux::region_note, "opt", "text", "32", "string up to length 32", ""  ],
	'city' => ["City", &libAux::city_note, "opt", "text", "32", "string up to length 32", "" ],
	'state' => ["State", &libAux::state_note, "opt", "text", "32", "string up to length 32", "" ],
	'orderdate' => ["Order Date", &libAux::order_date_note, "opt", "text", "10", "string of length 10 and takes the following format: [MM/DD/YYYY], (MM = month, DD = day, YYYY = year)", "validate_date(this.form.orderdate)" ],
	'rcvdate' => ["Received Date", &libAux::received_date_note, "opt", "text", "10", "string of length 10 and takes the following format:[MM/DD/YYYY], (MM = month, DD = day, YYYY = year)", "validate_date(this.form.rcvdate)" ],
	'rcvtime' => ["Received Time", &libAux::received_time_note, "opt", "text", "5", "string of length 5 and takes the following format: [HH:MM], (HH = hours, MM = minutes)", "validate_time(this.form.rcvtime)" ],
	'contact' => ["Contact", &libAux::contact_note, "opt", "text", "16", "string up to length 16", "" ],
	'comments' => ["Comments", &libAux::comments_note, "opt", "text", "32", "string up to length 32", "" ],
	'owner' => ["Owner", &libAux::owner_note, "opt", "text", "10", "format unknown", "" ],	 #FIXME: find OWNER format
	'group' => ["Group", &libAux::group_note, "opt", "text", "8", "string up to length 8", "" ],
	'access' => ["Access", &libAux::access_note, "opt", "select", [["AA", "All Read, All Write"], ["AG", "All Read, Group Write"], ["AO", "All Read, Owner Write"], ["GG", "Group Read, Group Write"], ["GO", "Group Read, Owner Write"], ["OO", "Owner Read, Owner Write"]], "GG", ""  ],
	'startdate' => ["Start Date", &libAux::start_date_note, "opt", "text", "10", "string of length 10 and takes the following format: [MM/DD/YYYY], (MM = month, DD = day, YYYY = year), (default = NOW)", "validate_date(this.form.startdate)" ],
	'starttime' => ["Start Time", &libAux::start_time_note, "opt", "text", "5", "string of length 5 and takes the following format: [HH:MM], (HH = hours, MM = minutes) (default = NOW)", "validate_time(this.form.starttime)" ],
	'stopdate' => ["Stop Date", &libAux::stop_date_note, "req", "text", "10", "It is a string of length ten and takes the following format: [MM/DD/YYYY], (MM = month, DD = day, YYYY = year)", "validate_date(this.form.stopdate)" ],
	'stoptime' => ["Stop Time", &libAux::stop_time_note, "req", "text", "5", "It is a string of length five and takes the following format: [HH:MM], (HH = hours, MM = minutes)", "validate_time(this.form.stoptime)" ],
	'tz' => ["Time Zone", &libAux::time_zone_note, "opt", "text", "30", "It a string up to length 30 (default = Local)", "" ],
	'ACTION' => ["Action", &libAux::action_note, "opt", "text", "8", "It is a string up to length 8; the value is fixed at NONE", "" ],
	'trclvl' => ["Trace Level", &libAux::trace_level_note, "opt", "select", [["0", "0"], ["1", "1"], ["2", "2"], ["3", "3"], ["4", "4"]], "0", "" ],
	'CISHOWTARGET' => ["CI Show Target", &libAux::CI_show_target_note, "opt", "select", \@yes_no, "Y", "" ],
	'CCSHOWTARGET' => ["CC Show Target", &libAux::CC_show_target_note, "opt", "select", [["REFNUM", "Ref Num"], ["TARGET", "Target"], ["EMPTY", "Empty"]], "EMPTY", "" ],
	'CISS' => ["CISS", &libAux::CISS_note, "opt", "select", \@yes_no, "Y", "" ],
	'COMBINED' => ["Combined", &libAux::combined_note, "opt", "select", \@yes_no, "Y", "" ],
	'MRP' => ["MRP", &libAux::MRP_note, "opt", "select", \@yes_no, "Y", "" ],
	'CPND' => ["CPND", &libAux::CPND_note, "opt", "select", \@yes_no, "Y", "" ],
	'PKTENV' => ["Packet Envelope Message", &libAux::PKTENV_note, "opt", "select", \@yes_no, "Y", "" ],
	'PKTCONT' => ["Packet Envelope Content", &libAux::PKTCONT_note, "opt", "select", \@yes_no, "Y", "" ],
	'BILL_NUM' => ["Billing Number", &libAux::BILL_NUM_note, "opt", "text", "24", "It is a string of 24 characters", "" ],
	'SO_ENCRYPTION' => ["Encryption", &libAux::ENCRYPTION_note, "opt", "select", [["NONE", "None"], ["RC4", "RC4"]], "NONE", "" ],
	'IOBS' => ["IOBS", &libAux::IOBS_note, "opt", "select", \@yes_no, "Y", "" ],
	'CRSS' => ["CRSS", &libAux::CRSS_note, "opt", "select", \@yes_no, "Y", "" ],
	'NCIS' => ["NCIS", &libAux::NCIS_note, "opt", "select", \@yes_no, "Y", "" ],
	'NCRS' => ["NCRS", &libAux::NCRS_note, "opt", "select", \@yes_no, "Y", "" ],
	'SO_KEY' => ["Key", &libAux::key_note, "opt", "text", "48", "It is a hexadecimal string up to length 48", "" ],
	'SERVTYPE' => ["Service Type", &libAux::service_type_note, "opt", "select", [["MSISDN", "MSISDN"], ["IMSI", "IMSI"], ["URI", "URI"]], "URI", "" ],
	'priority' => ["Priority", &libAux::priority_note, "opt", "text", "2", "Integer from 1 to 16", "validate_int_range(this.form.priority, 1, 16)" ],
	'afid' => ["AFID", &libAux::AFID_note, "req", "text", "16", "It is a string up to length 16", "" ],
	'TID' => ["TID", &libAux::TID_note, "req", "text", "5", "It is an unsigned integer between 1 and 10,000", "validate_int_range(this.form.TID, 1, 10000)" ],
	'JAREAID' => ["JAREAID", &libAux::JAREAID_note, "req", "text", "16", "It is a string of up to 16 characters", "" ],
	'destip' => ["Destination IP", &libAux::dest_IP_note, "req", "text", "20", "", "" ],
	'destport' => ["Destination Port", &libAux::dest_port_note, "req", "text", "5", "It is an unsigned integer between 1 and 65535", "" ],
	'CFID' => [ "CFID", &libAux::LEA_CFID_note, "req", "text", "16", "It is a string up to length 16", "" ],
	'version' => ["Version", &libAux::version_note, "opt", "select", [["2", "ATIS-1000678.2006"], ["3", "ATIS-1000678.a.2007"], ["4", "ATIS-1000678.b.2010"], ["0700005V2", "ATIS-0700005.a.2010"]], "2", "" ],
	'reqstate' => [ "Required State", &libAux::req_state_note, "req", "select", [["ACTIVE", "Active"], ["INACTIVE", "Inactive"]], "ACTIVE", ""  ],
	'connect_state' => [ "Connection State", &libAux::connect_state_note, "req", "select", [["ACTIVE", "Active"], ["INACTIVE", "Inactive"], ["FAILED", "Failed"]], "INACTIVE", ""  ],
	'ownip' => [ "Own IP", &libAux::own_IP_note, "req", "text", "20", "", "" ],
	'ownport' => ["Own Port", &libAux::own_port_note, "req", "text", "5", "It is an unsigned integer between 1000 and 65535 or 0. The system chooses the port number if ownport = 0 (default)", "" ],
	'filter' => [ "Filter", &libAux::filter_note, "req", "select", [["ALL", "All"], ["VO", "Only voice content is passed through"], ["VI", "Only video content is passed through"], ["VV", "Both voice and video content is passed through"]], "ALL", ""  ],
	'transport' => [ "Transport", &libAux::transport_note, "req", "select", [["TCP", "TCP"], ["UDP", "UDP"]], "TCP", ""  ],
	'if_ID' => ["IF ID", &libAux::if_ID_note, "req", "text", "1", "It is an unsigned integer between 1 and 5. Currently, only a value of 1 is supported", "" ],
);

# Initializes all variables
sub initiate {
	## Fields this interface requires be defined in the NODE/NODETYPE config files
	my @required_fields = ("NODEID", "NODETYPEID", "CLLI", "NODENAME", "PRIIP", "ACCESSTYPE", "PRILOGON", "PRIPASS");

	my $FB = libUtils::FB();	# font begin
	my $FE = libUtils::FE();        # font end

	$super_user = doCheckSuperUser();
	doSetGifs();

	# config changes
	%secondary_node_cfg_hash = libConfig::getCfgListHashByType("NODE", "NODETYPEID", "$secondary_node_type_ID");
	%primary_node_cfg_hash = libConfig::getCfgListHashByType("NODE", "NODETYPEID", "$primary_node_type_ID");

	my $req_fld_ref = \@required_fields;
	if (scalar keys %secondary_node_cfg_hash == 0 || scalar keys %primary_node_cfg_hash == 0) {
		doPrintGenHTMLException($FB . $secondary_node_type_ID . $FE, 3);
		return 1;
		# not reached
	} else {
		# check for required fields for the primary node
		foreach my $node_ID (sort keys %secondary_node_cfg_hash) {
			my ($status, $field) = valReqNodeFlds($secondary_node_cfg_hash{$node_ID}, $req_fld_ref);
			if ($status > 0) {
				doPrintGenHTMLException($FB . $secondary_node_type_ID . $FE, $status, $FB . $field . $FE);
				return 1;
				# not reached
			}
		}
		# check for required fields for the secondary node
		foreach my $node_ID (sort keys %primary_node_cfg_hash) {
			my ($status, $field) = valReqNodeFlds($primary_node_cfg_hash{$node_ID}, $req_fld_ref);
			if ($status > 0) {
				doPrintGenHTMLException($FB . $primary_node_type_ID . $FE, $status, $FB . $field . $FE);
				return 1;
				# not reached
			}
		}
	}

	return 0;
}

# prints the main part of the HTML including the initialization and HOST panel
sub displayXcipio {
	my @nodes = ();
	my @node_IPs = ();
	my @node_types = ();

	foreach my $node_ID (sort keys %secondary_node_cfg_hash) {
		my %anode = %{$secondary_node_cfg_hash{$node_ID}};
		push @nodes, "					<option value=\"$anode{NODEID}\">$anode{NODENAME}</option>";
		push @node_IPs, $anode{PRIIP};
		push @node_types, $anode{'NODETYPEID'};
	}

	foreach my $node_ID (sort keys %primary_node_cfg_hash) {
		my %anode = %{$primary_node_cfg_hash{$node_ID}};
		push @nodes, "					<option value=\"$anode{NODEID}\">$anode{NODENAME}</option>";
		push @node_IPs, $anode{PRIIP};
		push @node_types, $anode{'NODETYPEID'};
	}

	print "<script language=\"JavaScript\" type=\"text/javascript\">\n";
	print "var pddfIPs	 = [ \"", join("\", \"", @node_IPs), "\" ];\n";
	print "var node_types = [ \"", join("\", \"", @node_types), "\" ];\n";

	# print JavaScript functions
	printJSToggleWidget(\%fields);

	print <<Xcipio_HOST;

var panelID	= "p1"
var numDiv = 0;
var numRows	= 1
var tabsPerRow = 0;
var numLocations = numRows * tabsPerRow
var tabWidth = 60
var tabHeight = 30
var vOffset	= 8
var hOffset	= 10

var divLocation	= new Array(numLocations)
var newLocation	= new Array(numLocations)

for(var i=0; i<numLocations; ++i) {
	divLocation[i] = i
	newLocation[i] = i
}

	function display_node_info() {
		var form = document.forms[0];
		var host_index = form.NODEID.selectedIndex;
		var host_ID = form.NODEID.value;
		var host_type_ID = "";
		var node_actions = new Object();
		node_actions['0'] = "Add";
		node_actions['1'] = "Delete";
		node_actions['9'] = "List";

		if (host_index == -1 || host_index == 0) {
			form.PddfIP.value = "";
		} else {
			var IP_index = host_index - 1;
			var action = form.ACTIONTYPENUM;
			var object = form.object;
			var host_type_ID = node_types[IP_index];

			form.PddfIP.value = pddfIPs[IP_index];
			action.options.length = 0;	// clear action selection box
			object.options.length = 0;	// clear object selection box

			if (host_type_ID == "${secondary_node_type_ID}") {
				node_objects = new Array( "afwt" );
			} else if (host_type_ID == "${primary_node_type_ID}") {
				node_objects = new Array ( "co", "surveillance", "survopt", "target", "t1678cfci" );
			}

			// update actions selection list
			for (var value in node_actions) {
				var new_option = document.createElement("OPTION");
				new_option.text = node_actions[value];
				new_option.value = value;
				action.options.add(new_option);
			}

			// update objects selection list
			for (var i = 0; i < node_objects.length; i++) {
				var new_option = document.createElement("OPTION");
				new_option.text = node_objects[i];
				object.options.add(new_option);
			}
		}
	}

	function enableForm() {
		var add_action = "0";
		var delete_action = "1";
		var display_action = "9";

		var object_select = document.getElementById("object");

		disable_marks();

		if (object_select.selectedIndex < 0) {
			return;
		}

		var object = object_select.options[object_select.selectedIndex].text;

		var action_select = document.getElementById("ACTIONTYPENUM");
		var action = action_select.options[action_select.selectedIndex].value;

		// COID needed for all actions...
		set_mark("coid", "req");

		//... except display
		if (action == display_action) {
			set_mark("coid", "opt")
			return;
		}

		// only a subset of parameters are needed for delete
		if (action == delete_action) {
			if (object == "target" || object == "afwt") {
				set_mark("TID", "req");
			}

			if (object == "afwt") {
				set_mark("afid", "req");
			}

			if (object == "t1678cfci") {
				set_mark("if_ID", "req");
			}

			return;
		}

		if (object == "co") {
			set_mark("judge", "opt");
			set_mark("region", "opt");
			set_mark("city", "opt");
			set_mark("state", "opt");
			set_mark("orderdate", "opt");
			set_mark("rcvdate", "opt");
			set_mark("rcvtime", "opt");
			set_mark("contact", "opt");
			set_mark("comments", "opt");
			set_mark("owner", "opt");
			set_mark("group", "opt");
			set_mark("access", "opt");
		}

		if (object == "surveillance") {
			set_mark("caseid", "req");
			set_mark("CFID", "req");
			set_mark("stopdate", "req");
			set_mark("stoptime", "req");
			set_mark("startdate", "opt");
			set_mark("starttime", "opt");
			set_mark("tz", "opt");
			set_mark("SURVTYPE", "opt");
			set_mark("trclvl", "opt");
			set_mark("owner", "opt");
			set_mark("group", "opt");
			set_mark("access", "opt");
		}

		if (object == "survopt") {
			set_mark("location", "opt");
			set_mark("SMS", "opt");
			set_mark("CISHOWTARGET", "opt");
			set_mark("CISS", "opt");
			set_mark("CCSHOWTARGET", "opt");
			set_mark("COMBINED", "opt");
			set_mark("MRP", "opt");
			set_mark("CPND", "opt");
			set_mark("PKTENV", "opt");
			set_mark("PKTCONT", "opt");
			set_mark("DDE", "opt");
			set_mark("BILL_NUM", "opt");
			set_mark("SO_ENCRYPTION", "opt");
			set_mark("SO_KEY", "opt");
			set_mark("group", "opt");
			set_mark("owner", "opt");
			set_mark("access", "opt");
		}

		if (object == "target") {
			set_mark("SERVTYPE", "req");
			set_mark("serviceid", "req");
			set_mark("TID", "req");
			set_mark("group", "opt");
			set_mark("owner", "opt");
			set_mark("access", "opt");
		}

		if (object == "afwt") {
			set_mark("TID", "req");
			set_mark("afid", "req");
			set_mark("JAREAID", "opt");
			set_mark("comments", "opt");
			set_mark("group", "opt");
			set_mark("owner", "opt");
			set_mark("access", "opt");
		}

		if (object == "t1678cfci") {
			set_mark("if_ID", "req");
			set_mark("destip", "req");
			set_mark("destport", "req");
			set_mark("version", "opt");
			set_mark("reqstate", "opt");
			set_mark("ownip", "opt");
			set_mark("ownport", "opt");
			set_mark("trclvl", "opt");
			set_mark("filter", "opt");
			set_mark("comments", "opt");
			set_mark("transport", "opt");
		}
	}

	// sets the SULOGs hidden variable to the one in forms[0]
	function setSULOGs() {
		if ($super_user == 1) {
				document.forms[0].onSULOG.value = (document.forms[0].SULOG1.checked) ? "1" : 0;
		}
	}

 </script>
<script language="JavaScript1.2" src="/eleat/scheduler.js" type="text/javascript"></script>
<script language="JavaScript1.2" src="/eleat/dateTime.js" type="text/javascript"></script>
<SCRIPT language="JavaScript" type="text/javascript">
<!-- hide javascript
function scrollmessage(count) {

var m1 = "To add a trace, first add the COID, ";
var m2 = "then add the SURVEILLANCE and SURVEILLANCE OPTIONS, ";
var m3 = "then add the TARGET ";
var m4 = "";
var m5 = "";
var m6 = "You may use the UTILITIES Action Types to ";
var m7 = "display all traces in detail.";
var msg=m1+m2+m3+m4+m5+m6+m7;
var out = " ";
var c = 1;

if (count > 100)
{
	count--;
	cmd="scrollmessage("+seed+")";
	timerTwo=window.setTimeout(cmd,100);
}

else if (count <= 100 && count > 0)
{
	for (c=0 ; c < count ; c++)
	{
		out+=" ";
	}
	out+=msg;
	count--;
	window.status=out;
	cmd="scrollmessage("+count+")";
	timerTwo=window.setTimeout(cmd,100);
}

else if (count <= 0)
{
	if (-count < msg.length)
	{
		out+=msg.substring(-count,msg.length);
		count--;
		window.status=out;
		cmd="scrollmessage("+count+")";
		timerTwo=window.setTimeout(cmd,100);
		}
	else
	{
		window.status=" ";
		timerTwo=window.setTimeout("scrollmessage(100)",75);
		}
	}
}

// done hiding -->
</SCRIPT>

</head>

Xcipio_HOST
		;	###

	doPrintTrbshHeading("Generic", "CVOIP");

	print <<HIDDEN;
	<input type='hidden' name='DSPFMT' value='HTML'>
	<input type='hidden' name='from_www' value='yes'>
	<input type='hidden' name='node_type_ID' value='Xcipio'>
	<input type='hidden' name='node_type_txt' value='SS8 XCIPIO'>
	<input type='hidden' name='my_UI' value='/cgi-bin/uiTrbshCVoIP.cgi'>
	<input type='hidden' name='onSULOG' value='0'>
HIDDEN
	;

##############################################################
# Check to see if super user - if it is then print the
# checkbox for Transaction Logging.
##############################################################
	doPrintTransactionLog($super_user);

	print <<Xcipio_HOstyle_CONTINUE;

	<table cellspacing=1 cellpadding=1 align=center bgcolor="#efefff"
				 style="border-style:outset;">
	 <tr>
		<td nowrap align=center>
		 <table cellspacing=1 cellpadding=1 border=0>
			<tr valign=top align=center>
			<td nowrap align=right>
				<span>Action</span>
				<img name='markCOMMAND' SRC='${onMark}'>
			</td>
			<td nowrap align=left colspan=3>
				<select name=ACTIONTYPENUM id=ACTIONTYPENUM
				 onChange="enableForm();return true;">
				</select>
			</td>
			<td nowrap align=RIGHT>
				<span>Object</span>
				<img name='markCOMMAND' SRC='${onMark}'>
			</td>
			<td nowrap align=left colspan=3>
				<select name=object id=object
				 onChange="enableForm();return true;">
				</select>
			</td>
			</tr>
		 </table>

		 <fieldset>
			<legend class="class_legend" accesskey=N>SURVEILLANCE NODE</legend>
			<table cellspacing=1 cellpadding=1 border=0>
			 <tr>
				<td align="right" nowrap>
				 <span>Host Name</span>
				 <img name='markHOST' SRC='${onMark}'>
				</td>
				<td nowrap>
				 <select name="NODEID" onChange="display_node_info(); enableForm();">
					<option value="" selected="selected"></option>
Xcipio_HOstyle_CONTINUE
	;	###

	my $nodes = join "\n", @nodes;
	print $nodes;

	print <<Xcipio_FORM;
				 </select>
				</td>
				<td nowrap align=LEFT>
				 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;
				 <span>IP Address</span>
				 <img name='markPddfIP' SRC='${offMark}'>
				 <INPUT TYPE="text" name="PddfIP" SIZE="17" DISABLED=true
					TITLE='IP Address of the selected host'
					style="font-size:10pt;font-family:Arial;font-weight:normal;color:#4343ff;"
				</td>
			 </tr>
			</table>
		 </FIELDSET>
Xcipio_FORM
	;	###
}

# main
my $DBG_file = "$ELEATROOT/tmp/uiTrbshCVOIP.DBG";
libAux::debug_init($DBG_file);
my $init_ret = 0;

doPrintHTMLHeading("$secondary_node_type_ID Troubleshooting", 1);

%cgi = libUtils::getHTTPVars();
$DEBUG = $cgi{DEBUG};

$init_ret = initiate();

if ($init_ret == 0) {
	displayXcipio();
	printTOP();
	libWebUtils::gen_form(%fields);
	print_close_form();
	print_page_init_js();
	print_close_page();
}

exit 0;
