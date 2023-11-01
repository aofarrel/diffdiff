# this comparison will drop dashes!
import itertools
import sys

with open(sys.argv[1]) as pile_of_diffs:
    diffs = [line.strip("\n") for line in pile_of_diffs.readlines()]
    
black = '\033[30m'
red = '\033[91m'
end = '\033[0m'
highlight_cyan = '\u001b[48;5;87m'
highlight_green = '\u001b[48;5;47m'

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

all_bad_ones = []
for position in all_positions:
	highlight_this_position = False
	each_sample = []
	for sample in diffionaries:
		if position not in diffionaries[sample].keys():
			highlight_this_position = True
			if position not in all_bad_ones: all_bad_ones.append(position)
			each_sample.append(f"{red}-{black}")
		else:
			each_sample.append(diffionaries[sample][position])
	samples_at_this_position = ''.join(sample for sample in each_sample)

	if highlight_this_position:
		print(f"{highlight_cyan}{position}\t{''.join(sample for sample in each_sample)}{end}")
	elif not samples_at_this_position.count(samples_at_this_position[0]) == len(samples_at_this_position):
		print(f"{highlight_green}{position}\t{''.join(sample for sample in each_sample)}{end}")
	else:
		print(f"{position}\t{''.join(sample for sample in each_sample)}")

for sample, diff in diffionaries.items():
    print(f"{sample} calls {len(diff)} SNPs")

print(f"{len(all_bad_ones)} out of {len(all_positions)} positions have at least one mismatch")