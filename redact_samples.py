import argparse
import zipfile
import sys
import os

def build_denylist(remove_list_file) -> list:
	if not os.path.exists(remove_list_file):
		raise FileNotFoundError(f"Couldn't fine removal file {remove_list_file}")
	with open(remove_list_file, 'r') as f:
		to_remove_list = [line.strip() for line in f if line.strip()]
	to_remove_set = set(to_remove_list)
	print(f"Loaded {len(to_remove_set)} sample names to exclude ({len(to_remove_list)} including non-uniques)")
	return to_remove_list

def filter_from_combined_diff(input_file, to_remove, skip_checks) -> None:
	print("REMOVING FROM COMBINED DIFF FILE...")
	n_removals = 0
	n_kept = 0
	output_file = f"MODIFIED_{os.path.basename(input_file)}"
	delet_this = False

	with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
		for line in infile:
			if line.startswith('>'):
				sample_name = line[1:].rstrip('\r\n') # strip '>' and newline/carriage returns
				if sample_name in to_remove:
					n_removals += 1
					delet_this = True
				else:
					outfile.write(line)
					n_kept += 1
					delet_this = False
			elif not delet_this:
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
	print("REMOVING FROM SAMPLES_ADDED FILE...")
	n_removals = 0
	n_kept = 0
	output_file = f"MODIFIED_{os.path.basename(input_file)}"

	with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
		for line in infile:
			sample_name = line.rstrip('\r\n') # strip newline/carriage returns
			if sample_name in to_remove:
				n_removals += 1
			else:
				outfile.write(line)
				n_kept += 1				
	print(f"Processed {n_removals+n_kept} samples")
	print(f"Removed {n_removals} samples")
	if not skip_checks:
		if n_removals > len(to_remove):
			raise ValueError(f"Removed {n_removals} but only {len(to_remove)} on denylist; samples_added file likely contains duplicate samples")
		elif n_removals < len(to_remove):
			raise ValueError(f"Removed {n_removals} but there's {len(to_remove)} values on denylist")
	print(f"New samples_added file saved to: {output_file}")

def filter_from_set_table(input_zip, to_remove, skip_checks) -> None:
	print("REMOVING FROM SET DATA TABLE...")
	n_removals = 0
	n_kept = 0
	keep_current_sample = True
	extract_dir = "extracted_temp"
	with zipfile.ZipFile(input_zip, 'r') as zipped_table:
		zipped_table.extractall(extract_dir)
	extracted_files = [os.path.join(extract_dir, f) for f in os.listdir(extract_dir) if os.path.isfile(os.path.join(extract_dir, f))]
	assert len(extracted_files) == 2, f"Expected 2 files, but found {len(extracted_files)}"
	membership_file = next(f for f in extracted_files if f.endswith("set_membership.tsv"))
	output_file = f"MODIFIED_{os.path.basename(membership_file)}"

	with open(membership_file, 'r') as infile, open(output_file, 'w') as outfile:
		for line in infile:
			columns = line.rstrip('\r\n').split('\t')
			if len(columns) != 2:
				raise ValueError("Membership TSV doesn't have two columns, is it malformed?")
			if columns[1] not in to_remove:
				outfile.write(line)
				n_kept += 1
			else:
				n_removals += 1
			
	print(f"Processed {n_removals+n_kept} samples")
	print(f"Removed {n_removals} samples")
	if not skip_checks:
		if n_removals > len(to_remove):
			raise ValueError(f"Removed {n_removals} but only {len(to_remove)} on denylist; set membership table likely contains duplicate samples")
		elif n_removals < len(to_remove):
			raise ValueError(f"Removed {n_removals} but there's {len(to_remove)} values on denylist")
	print(f"New set membership file saved to: {output_file}")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="redact_samples.py"
	"\n\nRedact samples from a combined diff file, a samples added file, and/or a set data table. If you're using this for "
	"\nTree Nine, you may need to run with --looseygoosey if the set data table contains duplicate membership and/or contans "
	"\nsamples Tree Nine hasn't processed yet. You could instead make two denylists: one for samples that have already "
	"\nbeen processed by Tree Nine for --combined_diff_file and --samples_added_file, and one for all samples on the set "
	"\ndata table (although duplicate membership on the set table may still trigger an assert without --looseygoosey)",
	formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument(
		"denylist", 
		help="Path to the newline-delimited text file containing sample names to remove"
	)
	parser.add_argument(
		"--combined_diff_file",
		nargs="?", 
		default=None, 
		help="Path to the concatenated diff file (outfile will be MODIFIED_ + this file's basename)"
	)
	parser.add_argument(
		"--samples_added_file", 
		nargs="?", 
		default=None, 
		help="Optional: Path to the samples added file (samples_addedYYYY-MM-DD); if you're using Tree Nine you need this"
	)
	parser.add_argument(
		"--set_data_table_zip", 
		nargs="?", 
		default=None, 
		help="Optional: Path to the **set** data table **zip**; if you're using Tree Nine you might need this"
	)
	parser.add_argument(
		"--looseygoosey", 
		action="store_true", 
		dest="skip_checks",
		help="Bypass validation checks"
	)
	args = parser.parse_args()
	to_remove = build_denylist(args.denylist)
	if args.combined_diff_file:
		filter_from_combined_diff(args.combined_diff_file, to_remove, args.skip_checks)
	if args.samples_added_file is not None:
		filter_from_samples_added(args.samples_added_file, to_remove, args.skip_checks)
	if args.set_data_table_zip is not None:
		filter_from_set_table(args.set_data_table_zip, to_remove, args.skip_checks)

