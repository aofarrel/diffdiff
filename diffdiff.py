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
	#this_diff = {keys[i]: values[i] for i in range(len(keys)) if values != "-"} # the check isn't working properly
	this_diff = {keys[i]: values[i] for i in range(len(keys))}
	this_stripped_diff = {}
	for key in this_diff:
		if this_diff[key] != '-':
			this_stripped_diff[key] = this_diff[key]
	diffionaries[diff] = this_stripped_diff
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





### bad idea zone ###



# there are better ways of doing this...
def compare_two_diffs(a_diff, b_diff, a_sample, b_sample):
	for position in a_diff:
		if position not in b_diff.keys():
			print(f"{a_sample} calls {a_diff[position]} but {b_sample} has no info at {position}")
		elif a_diff[position] != b_diff[position]:
			(f"{a_sample} calls {a_diff[position]} but {b_sample} calls {b_diff[position]}")
		else:
			pass
	print("\n")
	#differences = a_diff.get(key) == value for key, value in b_diff.items()
	#for thing in differences:
	#	print(thing)

x = diffs[0].strip(".diff")
y = diffs[1].strip(".diff")
z = diffs[2].strip(".diff")
w = diffs[3].strip(".diff")

# compare_two_diffs(diffionaries[x], diffionaries[y],x, y)
# compare_two_diffs(diffionaries[x], diffionaries[z],x, z)
# compare_two_diffs(diffionaries[x], diffionaries[w],x, w)

# compare_two_diffs(diffionaries[y], diffionaries[x],y, x) # inverse
# compare_two_diffs(diffionaries[y], diffionaries[z],y, z)
# compare_two_diffs(diffionaries[y], diffionaries[w],y, w)

# compare_two_diffs(diffionaries[z], diffionaries[x],z, x) # inverse
# compare_two_diffs(diffionaries[z], diffionaries[y],z, y) # inverse
# compare_two_diffs(diffionaries[z], diffionaries[w],z, w)

# compare_two_diffs(diffionaries[w], diffionaries[x],w, x) # inverse
# compare_two_diffs(diffionaries[w], diffionaries[y],w, y) # inverse
# compare_two_diffs(diffionaries[w], diffionaries[z],w, z) # inverse

# for i in range(0, len(diffs)):
# 	this_sample_key = diffs[i].strip(".diff")
# 	this_sample_dic = diffionaries[this_sample_key]
# 	next_sample_key = diffs[i+1].strip(".diff")
# 	next_sample_dic = diffionaries[next_sample_key]
# 	for position in this_sample_dic:
# 		if position not in next_sample_dic.keys():
# 			print(f"{this_sample_key} calls {this_sample_dic[position]} but {next_sample_key} has no info at {position}")
# 		#if this_sample_dic.get(position) not in next_sample_dic.keys():
# 		#	print(f"{next_sample_key} has no info at {position}")
# 		elif this_sample_dic[position] != next_sample_dic[position]:
# 			(f"{this_sample_key} calls {this_sample_dic[position]} but {next_sample_key} calls {next_sample_dic[position]}")
# 		else:
# 			print("same")
# 	#differences = this_sample_dic.get(key) == value for key, value in next_sample_dic.items()
# 	#for thing in differences:
# 	#	print(thing)