# this comparison will drop dashes!
# pylint: disable=W0311,W1514,C0103,C0321,C0301

import sys

with open(sys.argv[1]) as pile_of_diffs:
	diffs = [line.strip("\n") for line in pile_of_diffs.readlines()]
backmask = sys.argv[2]

BLACK = '\033[30m'
RED = '\033[91m'
END = '\033[0m'
HIGHLIGHT_CYAN = '\u001b[48;5;87m'
HIGHLIGHT_GREEN = '\u001b[48;5;47m'

diffionaries = {}
for diff in diffs:
	with open(diff, "r") as f:
		sample = f.readline().strip().strip(">")
		data = f.readlines()[1:]
	keys = [int(line.split()[1]) for line in data]   # position is unique, so they are the keys
	values = [str(line.split()[0]) for line in data] # SNPs are not unique
	this_diff = {keys[i]: values[i] for i in range(len(keys)) if values[i] != "-"}
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
	highlight_this_position = False
	each_sample = []
	for sample, positions in diffionaries.items():
		if position not in positions.keys():
			highlight_this_position = True
			if position not in incongruent_positions: incongruent_positions.append(position)
			each_sample.append(f"{RED}-{BLACK}")
		else:
			each_sample.append(positions[position])
	samples_at_this_position = ''.join(sample for sample in each_sample)

	# print in place -- likely more efficient then going back later
	if highlight_this_position:
		print(f"{HIGHLIGHT_CYAN}{position}\t{''.join(sample for sample in each_sample)}{END}")
	elif samples_at_this_position.count(samples_at_this_position[0]) != len(samples_at_this_position):
		print(f"{HIGHLIGHT_GREEN}{position}\t{''.join(sample for sample in each_sample)}{END}")
	else:
		print(f"{position}\t{''.join(sample for sample in each_sample)}")

for sample, diff in diffionaries.items():
	print(f"{sample} calls {len(diff)} SNPs")

print(f"{len(incongruent_positions)} out of {len(all_positions)} positions have at least one mismatch")

if backmask:
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
		print(f"For {input_diff_file}, backmasked {len(this_sample_backmasked)} positions at: {this_sample_backmasked}")
