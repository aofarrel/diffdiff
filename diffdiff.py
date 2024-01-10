# pylint: disable=W0311,W1514,C0103,C0321,C0301


# TODO: when not dropping dashes, dashes that are made to cover multiple positions get turned into just one

import argparse

BLACK = '\033[30m'
RED = '\033[91m'
END = '\033[0m'
HIGHLIGHT_CYAN = '\u001b[48;5;87m'
HIGHLIGHT_GREEN = '\u001b[48;5;47m'
HIGHLIGHT_GRAY = '\u001b[48;5;250m'

parser = argparse.ArgumentParser(description="diffdiff - diff your diff files")
parser.add_argument("input_file_with_diff_paths",
	help="Input file listing paths of diff files to compare, one path per line")
parser.add_argument("-b", "--backmask", action="store_true",
	help="Create new diff files masked at at locations where at least one sample is masked (see docs)")
parser.add_argument("-ao", "--alignment_outfile", default=None, required=False,
	help="Filename of alignment (if not defined, print to stdout)")
parser.add_argument("-c", "--colors", action="store_true",
	help=f"Highlight SNP-ref mismatches in {HIGHLIGHT_CYAN}cyan{END} and SNP-SNP mismatches in {HIGHLIGHT_GREEN}green{END}, "
	f"with specific positions marked in {RED}red{END}")
parser.add_argument("-i", "--ignore_masks", action="store_true",
	help="Ignore masked positions. This effectively makes masked positions and ref positions get treated the same.")
parser.add_argument("-v", "--verbose", action="store_true",
	help="List all positions that get backmasked and print an alignment of backmasked diffs (no effect if not backmasking)")
args = parser.parse_args()

C_BLACK = BLACK if args.colors else ''
C_RED = RED if args.colors else ''
C_END = END if args.colors else ''
C_HIGHLIGHT_CYAN = HIGHLIGHT_CYAN if args.colors else ''
C_HIGHLIGHT_GREEN = HIGHLIGHT_GREEN if args.colors else ''
C_HIGHLIGHT_GRAY = HIGHLIGHT_GRAY if args.colors else ''

class Diff:
	def __init__(self, path: str, sample: str, data: dict):
		self.path = path  # previously acted as the key in diffionaries
		self.sample = sample
		self.data = data

def write_line(line):
	if args.alignment_outfile:  # ie, if not None
		with open(args.alignment_outfile, "a") as f:
			f.write(line+"\n")
	else:
		print(line)


diffionaries = []

with open(args.input_file_with_diff_paths) as pile_of_diffs:
	diff_files = [line.strip("\n") for line in pile_of_diffs.readlines()]

for diff_file in diff_files:
	with open(diff_file, "r") as input_diff:
		sample_name = input_diff.readline().strip().strip(">") # after this readline() we are now at the first (0th) SNP position
		diff_data = input_diff.readlines()                     # read all remaining (eg, all non-sample) lines
	keys = [int(line.split()[1]) for line in diff_data]   # position is unique, so they are the keys
	values = [str(line.split()[0]) for line in diff_data] # SNPs are not unique
	if args.ignore_masks:
		this_diff = Diff(diff_file, sample_name, {keys[i]: values[i] for i in range(len(keys)) if values[i] != "-"})
	else:
		this_diff = Diff(diff_file, sample_name, {keys[i]: values[i] for i in range(len(keys))})
	diffionaries.append(this_diff)
print(f"Converted {len(diff_files)} diffs to dictionaries.")

all_positions = []
for i in range(0, len(diffionaries)):
	this_sample = diffionaries[i]
	for position in this_sample.data:
		if position not in all_positions:
			all_positions.append(position)

incongruent_positions = []
snp_incongrence_positions = []     # eg, one sample is ref and another is C SNP, or one is G SNP and another is T SNP
masked_incongruence_positions = [] # eg, one sample is G SNP and another is masked, or (if !ignore_masks) one is ref and another is masked
masked_total_positions = []        # masked_incongruence + positions where ALL samples get masked
for position in all_positions:
	missing_data = False
	each_sample = []
	for input_diff in diffionaries:
		if position not in input_diff.data.keys():
			# if data for this position is not in the current sample
			if args.ignore_masks:
				# this position is missing information either because it is ref or masked
				missing_data = True
				each_sample.append(f"{C_RED}?{C_BLACK}")  # purposely not using END so the highlight continues
			else:
				# this sample is missing information because it is ref
				each_sample.append(f"{C_RED}R{C_BLACK}")  # purposely not using END so the highlight continues
		else:
			each_sample.append(input_diff.data[position])
	samples_at_this_position = ''.join(sample for sample in each_sample)

	# print in place -- likely more efficient then going back later
	if missing_data:
		# This position is masked in AT LEAST ONE sample, and ignore_masks is true
		if position not in incongruent_positions: incongruent_positions.append(position)
		if position not in masked_incongruence_positions: masked_incongruence_positions.append(position)
		write_line(f"{C_HIGHLIGHT_CYAN}{position}\t{''.join(sample for sample in each_sample)}{C_END}")
	elif "-" in samples_at_this_position and not missing_data:
		# This position is masked in AT LEAST ONE sample, and ignore_masks is false
		if position not in incongruent_positions: incongruent_positions.append(position)
		if position not in masked_total_positions: masked_total_positions.append(position)
		if ''.join(sample for sample in each_sample) != ''.join("-" for sample in each_sample):
			# This position is masked in ALL samples, and ignore_masks is false
			if position not in masked_incongruence_positions: masked_incongruence_positions.append(position)
			write_line(f"{C_HIGHLIGHT_GRAY}{position}\t{''.join(sample for sample in each_sample)}{C_END}")
		else:
			# This position is masked in 1≤x≤n-1 samples
			write_line(f"{position}\t{''.join(sample for sample in each_sample)}")
	elif samples_at_this_position.count(samples_at_this_position[0]) != len(samples_at_this_position):
		# TODO: This seems to be a perfectly functional SNP-mismatch checker, but I don't actually
		# remember HOW it works.
		if position not in incongruent_positions: incongruent_positions.append(position)
		if position not in snp_incongrence_positions: snp_incongrence_positions.append(position)
		write_line(f"{C_HIGHLIGHT_GREEN}{position}\t{''.join(sample for sample in each_sample)}{C_END}")
	else:
		write_line(f"{position}\t{''.join(sample for sample in each_sample)}")

for input_diff in diffionaries:
	if args.ignore_masks:
		print(f"{input_diff.sample} has {len(input_diff.data)} non-reference SNPs")
	else:
		print(f"{input_diff.sample} has {len(input_diff.data)} non-reference SNPs and masked positions")

assert len(incongruent_positions) == len(set(incongruent_positions))
assert len(snp_incongrence_positions) == len(set(snp_incongrence_positions))
assert len(masked_incongruence_positions) == len(set(masked_incongruence_positions))
assert len(masked_total_positions) == len(set(masked_total_positions))
assert len(masked_total_positions) + len(snp_incongrence_positions) == len(incongruent_positions)

print(f"\nComparing across all diffs:\n{len(incongruent_positions)} out of {len(all_positions)} positions have at least one mismatch or mask.")
print(f"\t{len(snp_incongrence_positions)} positions are SNP mismatches")
print(f"\t{len(masked_incongruence_positions)} positions have a mask-nomask mismatch")
print(f"\t{len(masked_total_positions) - len(masked_incongruence_positions)} positions are masked across all samples")

if args.backmask:
	backmasked_diffs = []
	for input_diff_object in diffionaries:
		if args.verbose: print(f"Backmasking {input_diff_object.sample}...")
		backmasked_positions = []
		retained_positions = []
		output_data = {}
		for position in masked_incongruence_positions:
			if position not in input_diff_object.data.keys():
				if args.verbose: print(f"Masking reference call at position {position}")
				output_data[position] = "-"
				backmasked_positions.append(position)
			elif input_diff_object.data[position] != "-":
				if args.verbose: print(f"Masking {input_diff_object.data[position]} SNP at position {position}")
				output_data[position] = "-"
				backmasked_positions.append(position)
			else:
				print(f"Leaving {input_diff_object.data[position]} in place at position {position}")
				output_data[position] = input_diff_object.data[position]
				retained_positions.append(position)
		for position in input_diff_object.data.keys():
			if position not in output_data.keys():
				output_data[position] = input_diff_object.data[position]
		new_diff_path = f"{input_diff_object.path}.backmask.diff"
		new_diff_sample = f"[BM]{input_diff_object.sample}"
		new_diff_data = dict(sorted(output_data.items()))
		new_diff = Diff(new_diff_path, new_diff_sample, new_diff_data)
		backmasked_diffs.append(new_diff)

		with open(new_diff.path, "w") as backmasked_diff:
			backmasked_diff.write(f">{new_diff.sample}\n")
			for position in new_diff.data.keys():
				backmasked_diff.write(f"{new_diff.data[position]}\t{position}\t1\n")
		print(f"For {new_diff.sample}, backmasked {len(backmasked_positions)} positions: ")
		print(*backmasked_positions, end="\n\n")
	
	print("New realignment of backmasked diffs:")
	for position in all_positions:
		each_sample = []
		for backmasked_diff in backmasked_diffs:
			if position not in backmasked_diff.data.keys():
				# if data for this position is not in the current sample
				if args.ignore_masks:
					# this position is missing information either because it is ref or masked
					each_sample.append(f"{C_RED}?{C_BLACK}")  # purposely not using END so the highlight continues
				else:
					# this sample is missing information because it is ref
					each_sample.append(f"{C_RED}R{C_BLACK}")  # purposely not using END so the highlight continues
			else:
				each_sample.append(backmasked_diff.data[position])
		samples_at_this_position = ''.join(sample for sample in each_sample)
		print(f"{position}\t{samples_at_this_position}")
