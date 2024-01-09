# this comparison will drop dashes!
# pylint: disable=W0311,W1514,C0103,C0321,C0301

import argparse

BLACK = '\033[30m'
RED = '\033[91m'
END = '\033[0m'
HIGHLIGHT_CYAN = '\u001b[48;5;87m'
HIGHLIGHT_GREEN = '\u001b[48;5;47m'
HIGHLIGHT_GRAY = '\u001b[100m'

parser = argparse.ArgumentParser(description="diffdiff - diff your diff files")
parser.add_argument("input_file_with_diff_paths",
	help="Input file listing paths of diff files to compare, one path per line")
parser.add_argument("-b", "--backmask", action="store_true",
	help="Create new diff files masked at at locations where all diffs call either the same SNP or reference (see docs)")
parser.add_argument("-ao", "--alignment_outfile", default=None, required=False,
	help="Filename of alignment (if not defined, print to stdout)")
parser.add_argument("-c", "--colors", action="store_true",
	help=f"Highlight SNP-ref mismatches in {HIGHLIGHT_CYAN}cyan{END} and SNP-SNP mismatches in {HIGHLIGHT_GREEN}green{END}, "
	f"with specific positions marked in {RED}red{END}")
parser.add_argument("-d", "--drop_masks", action="store_true",
	help="Drop masked positions. This effectively makes masked positions and ref positions get treated the same.")
args = parser.parse_args()

C_BLACK = BLACK if args.colors else ''
C_RED = RED if args.colors else ''
C_END = END if args.colors else ''
C_HIGHLIGHT_CYAN = HIGHLIGHT_CYAN if args.colors else ''
C_HIGHLIGHT_GREEN = HIGHLIGHT_GREEN if args.colors else ''
C_HIGHLIGHT_GRAY = HIGHLIGHT_GRAY if args.colors else ''

with open(args.input_file_with_diff_paths) as pile_of_diffs:
	diffs = [line.strip("\n") for line in pile_of_diffs.readlines()]

def write_line(line):
	if args.alignment_outfile:  # ie, if not None
		with open(args.alignment_outfile, "a") as f:
			f.write(line+"\n")
	else:
		print(line)

diffionaries = {}
for diff in diffs:
	with open(diff, "r") as input_diff:
		sample = input_diff.readline().strip().strip(">")
		data = input_diff.readlines()[1:]
	keys = [int(line.split()[1]) for line in data]   # position is unique, so they are the keys
	values = [str(line.split()[0]) for line in data] # SNPs are not unique
	if args.drop_masks:
		this_diff = {keys[i]: values[i] for i in range(len(keys)) if values[i] != "-"}
	else:
		this_diff = {keys[i]: values[i] for i in range(len(keys))}
	diffionaries[diff] = this_diff
print(f"Converted {len(diffs)} diffs to dictionaries.")

all_positions = []
for i in range(0, len(diffs)):
	this_sample_key = diffs[i]
	this_sample_dic = diffionaries[this_sample_key]
	for position in this_sample_dic:
		if position not in all_positions:
			all_positions.append(position)

incongruent_positions = []
for position in all_positions:
	missing_data = False
	each_sample = []
	for sample, positions in diffionaries.items():
		if position not in positions.keys():
			# if data for this position is not in the current sample
			if position not in incongruent_positions: incongruent_positions.append(position)
			if args.drop_masks:
				# this position is missing information either because it is ref or masked
				missing_data = True
				each_sample.append(f"{C_RED}?{C_BLACK}")  # purposely not using END so the highlight continues
			else:
				# this sample is missing information because it is ref
				each_sample.append(f"{C_RED}R{C_BLACK}")  # purposely not using END so the highlight continues
		else:
			each_sample.append(positions[position])
	samples_at_this_position = ''.join(sample for sample in each_sample)

	# print in place -- likely more efficient then going back later
	if missing_data:
		write_line(f"{C_HIGHLIGHT_CYAN}{position}\t{''.join(sample for sample in each_sample)}{C_END}")
	elif "-" in samples_at_this_position and not missing_data:
		write_line(f"{C_HIGHLIGHT_GRAY}{position}\t{''.join(sample for sample in each_sample)}{C_END}")
	elif samples_at_this_position.count(samples_at_this_position[0]) != len(samples_at_this_position):
		write_line(f"{C_HIGHLIGHT_GREEN}{position}\t{''.join(sample for sample in each_sample)}{C_END}")
	else:
		write_line(f"{position}\t{''.join(sample for sample in each_sample)}")

for sample, diff in diffionaries.items():
	print(f"{sample} calls {len(diff)} SNPs")

print(f"\n{len(incongruent_positions)} out of {len(all_positions)} positions have at least one mismatch.\n")


#### add information about which mismatch is which





if args.backmask:
	for input_diff_file in diffs:
		this_sample_dic = diffionaries[input_diff_file]
		this_sample_backmasked = []
		with open(f"{input_diff_file}.backmask.diff", "w") as backmasked_diff:
			for position in this_sample_dic:
				if position in incongruent_positions:
				  backmasked_diff.write(f"-\t{position}\t1\n")
				  this_sample_backmasked.append(position)
				else:
				  backmasked_diff.write(f"{this_sample_dic[position]}\t{position}\t1\n")
		print(f"For {input_diff_file}, backmasked {len(this_sample_backmasked)} positions: ")
		print(*this_sample_backmasked, end="\n\n")
