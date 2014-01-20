# libWebUtils.pm
# Library for web string constants and web specifics.
# Usage:  use libs::libWebUtils;
# Created by Paul Ireifej 12/27/2012
#

use strict;
use warnings;
use libs::libAux;
package libWebUtils;

our %mark_src = (
	'req' => "/images/checkmark.gif",
	'off' => "/images/xmark.gif",
	'opt' => "/images/omark.gif"
);

#
# gen_form()
# Generate the HTML & javascript for a troubleshooting form.
# Arg 0 is a hash of arrays, each of which describes a single input field to be displayed.
# The array has the following format:
#		- key - used as the base for the IDs and names
#		- field 1 - text for the label
#		- field 2 - tool tip for the label
#		- field 3 - mark source (req, off, opt)
#		- field 4 - type of input: text field or selection box (text, select)
#		If text box type:
#			- field 5 - maximum length of input (number of characters)
#			- field 6 - tool tip (HTML title property)
#		If select type:
#			- field 5 - array of selection options (each a 2-element array)
#			- field 6 - option to select by default
#		- field 7 (for both text & select) - an "onChange" string (usually javascript)
# The optional second arg (arg1) is an array of IDs.
# When present, it is used to determine the order in which
# the objects are displayed.  Otherwise the (semi-random) order
# of the hash keys is used.
#
sub gen_form(\%;\@) {
	my %args = %{$_[0]};
	my @IDs = (defined($_[1])) ? @{$_[1]} : keys(%args);
	my $count = 0;

	# If the caller provides an ordering array, it MUST include all & only the fields present in %args
	# (or else Bad Things happen in the resulting page's javascript) - so we confirm their alignment here.
	if (defined($_[1])) {
		my %req_names = %args;	# make a copy we can scribble on
		foreach my $field_name (@IDs) {
			if (! defined($req_names{$field_name})) {
				libAux::croak(1, "libWebUtils::gen_form: Error: $field_name is present in the ordering array in arg 1 but not in the field definitions in arg 0 (or present in the array twice)");
				# not reached
			}
			delete($req_names{$field_name});
		}
		if (keys(%req_names) > 0) {
			my $leftovers = join(', ', keys(%req_names));
			libAux::croak(1,
				"libWebUtils::gen_form: Error: the following fields from arg 0 are missing from the ordering array in arg 1: '$leftovers'");
			# not reached
		}
	}
	print <<UL
	<div id="arguments" style="z-index:11">
		<ul>
UL
	;

	foreach my $ID (@IDs) {
		$count++;
		my ($label_text, $label_tool_tip, $mark_src_value, $type, $input_prop, $input_supp, $on_change_str) = @{$args{$ID}};
		if (! defined($on_change_str)) {
			libAux::croak(1, "libWebUtils::gen_form: Error: too few fields in row '$ID' of arg 0");
			# not reached
		}
		my $mark_src_path = $mark_src{$mark_src_value};

		# print label
		print <<LABEL
			<li class="class_li" align="right" nowrap name="td_${ID}" id="td_${ID}">
				<span class="class_span" name='label_${ID}' id='label_${ID}'
					title='${label_tool_tip}'
					style='font-size:10pt; font-weight:bold;'>${label_text}</span>
				<img name='mark_${ID}' id='mark_${ID}' src='${mark_src_path}'/>
LABEL
		;
		my $on_change = ($on_change_str ne "") ? "onChange=\"$on_change_str\" " : "";	# note trailing " "
		if ($type eq "text") {
			# print text box input
			print <<TEXT
				<input class="class_input" type="text" name="${ID}" id="${ID}" value=""
					size="${input_prop}" maxlength="${input_prop}" style="font-size:10pt;"
					title="${input_supp}"
					${on_change}tabindex="$count">
TEXT
			;
		} elsif ($type eq "select") {
			# print selection box input
			print <<SELECT
				<select class="class_input" name="${ID}" id="${ID}" style="font-size:10pt;" ${on_change}tabindex="$count">
SELECT
			;

			my @options = @{$input_prop};
			foreach my $option (@options) {
				my ($option_value, $option_text) = @$option;
				if ($option_value eq $input_supp) {
					print <<OPTION
						<option value=${option_value} selected="SELECTED">${option_text}</option>
OPTION
					;
				} else {
					print <<OPTION
						<option value=${option_value}>${option_text}</option>
OPTION
					;
				}
			}
			print <<SELECT
				</select>
SELECT
			;
		} else {
			print "error: unknown element type '$type'\n";
			libAux::croak(1, "libWebUtils::gen_form: Error: unknown element type ''$type' in row $ID");
			# not reached
		}

		print <<OPTION
			</li>
OPTION
		;
	}

	print <<TABLE
		</ul>
	</div>
TABLE
	;
} # end gen_form()

1;
