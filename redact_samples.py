import argparse
import sys
import os

def build_denylist(remove_list_file) -> set:
	if not os.path.exists(remove_list_file):
		raise FileNotFoundError(f"Couldn't fine removal file {remove_list_file}")
	with open(remove_list_file, 'r') as f:
		to_remove = {line.strip() for line in f if line.strip()}
	print(f"Loaded {len(to_remove)} sample names to exclude")
	return to_remove

def filter_from_combined_diff(input_file, to_remove, skip_checks) -> None:
	n_removals = 0
	n_kept = 0
	keep_current_sample = True
	output_file = f"MODIFIED_{os.path.basename(input_file)}"

	with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
		for line in infile:
			if line.startswith('>'):
				sample_name = line[1:].rstrip('\r\n') # strip '>' and newline/carriage returns
				
				if sample_name in to_remove:
					keep_current_sample = False
					n_removals += 1
				else:
					keep_current_sample = True
					n_kept += 1
			
			if keep_current_sample:
				outfile.write(line)

	print(f"Processed {n_removals+n_kept} samples")
	print(f"Removed {n_removals} samples")
	if not skip_checks:
		if n_removals > len(to_remove):
			raise ValueError(f"Removed {n_removals} but only {len(to_remove)} on denylist; combined diff file likely contains duplicate samples")
		elif n_removals < len(to_remove):
			raise ValueError(f"Removed {n_removals} but there's {len(to_remove)} values on denylist")
	print(f"New diff file saved to: {output_file}")

def filter_from_samples_added(input_file, to_remove, skip_checks) -> None:
	n_removals = 0
	n_kept = 0
	keep_current_sample = True
	output_file = f"MODIFIED_{os.path.basename(input_file)}"

	with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
		for line in infile:
			sample_name = line.rstrip('\r\n') # strip newline/carriage returns
			if sample_name in to_remove:
				keep_current_sample = False
				n_removals += 1
			else:
				keep_current_sample = True
				n_kept += 1
			if keep_current_sample:
				outfile.write(line)
	print(f"Processed {n_removals+n_kept} samples")
	print(f"Removed {n_removals} samples")
	if not skip_checks:
		if n_removals > len(to_remove):
			raise ValueError(f"Removed {n_removals} but only {len(to_remove)} on denylist; samples_added file likely contains duplicate samples")
		elif n_removals < len(to_remove):
			raise ValueError(f"Removed {n_removals} but there's {len(to_remove)} values on denylist")
	print(f"New samples_added file saved to: {output_file}")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Filter out denylisted samples from a concatenated diff file")
	parser.add_argument(
		"combined_diff_file", 
		help="Path to the concatenated diff file (outfile will be MODIFIED_ + this file's basename)"
	)
	parser.add_argument(
		"denylist", 
		help="Path to the newline-delimited text file containing sample names to remove"
	)
	parser.add_argument(
		"samples_added_file", 
		nargs="?", 
		default=None, 
		help="Optional: Path to the samples added file (samples_addedYYYY-MM-DD); if you're using Tree Nine you need this"
	)
	parser.add_argument(
		"set_data_table", 
		nargs="?", 
		default=None, 
		help="Optional: Path to the **set** data table TSV; if you're using Tree Nine you might need this"
	)
	parser.add_argument(
		"--looseygoosey", 
		action="store_true", 
		dest="skip_checks",
		help="Bypass validation checks"
	)
	args = parser.parse_args()
	to_remove = build_denylist(args.denylist)
	filter_from_combined_diff(args.combined_diff_file, to_remove, args.skip_checks)
	if args.samples_added_file is not None:
		filter_from_samples_added(args.samples_added_file, to_remove, args.skip_checks)
	#if args.set_data_table is not None:
	#	filter_from_data_table(args.set_data_table, to_remove, args.skip_checks)

