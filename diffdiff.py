# pylint: disable=W0311,W1514,C0103,C0321,C0301

import argparse
try:
	from tqdm import tqdm
except ImportError:
	print("Failed to import tqdm")


BLACK_LIGHT_BG = '\033[82m'
HIGHLIGHT_CYAN_LIGHT_BG = '\u001b[48;5;87m'
HIGHLIGHT_GREEN_LIGHT_BG = '\u001b[48;5;47m'
HIGHLIGHT_GRAY_LIGHT_BG = '\u001b[48;5;250m'

BLACK_DARK_BG = '\033[97m'
HIGHLIGHT_CYAN_DARK_BG = '\u001b[48;5;75m'
HIGHLIGHT_GREEN_DARK_BG = '\u001b[48;5;70m'
HIGHLIGHT_GRAY_DARK_BG = '\u001b[48;5;239m'

END = '\033[0m'
FADE = '\u001b[48;2;250m'
RED = '\033[91m'            # TODO: this might be terrible for RG colorblindness

parser = argparse.ArgumentParser(description="diffdiff - diff your diff files")
parser.add_argument("input_file_with_diff_paths",
	help="Input file listing paths of diff files to compare, one path per line")
parser.add_argument("-b", "--backmask", action="store_true",
	help="Create new diff files masked at positions where at least one sample is masked")
parser.add_argument("-ao", "--alignment_outfile", default=None, required=False,
	help="Outfile of alignment")
parser.add_argument("-mo", "--mask_outfile", default=None, required=False,
	help="Outfile TSV of positions where at least one sample is masked -- designed for matUtils mask")
parser.add_argument("-no", "--noteworthy_outfile", default=None, required=False,
	help="Outfile of noteworthy alignments (SNP-SNP mismatch, SNP-ref mismatch, SNP-mask mismatch)")
parser.add_argument("-so", "--summary_outfile", default=None, required=False,
	help="Outfile of summary information")
parser.add_argument("-c", "--colors", action="store_true",
	help=f"[for black-background terminals try also using -l] Highlight SNP-SNP mismatches in {HIGHLIGHT_CYAN_LIGHT_BG}cyan{END}, "
	f"SNP-ref mismatches in {HIGHLIGHT_GREEN_LIGHT_BG}green{END}, "
	f"and places where at least one sample is masked in {HIGHLIGHT_GRAY_LIGHT_BG}gray{END}")
parser.add_argument("-l", "--light", action="store_true",
	help=f"[not needed if not -c] Adjusts -c to work better on black-background terminals." 
	f"SNP-SNP mismatches: {HIGHLIGHT_CYAN_DARK_BG}TGGG{END} "
	f"SNP-ref mismatches: {HIGHLIGHT_GREEN_DARK_BG}T{RED}RR{BLACK_DARK_BG}T{END} "
	f"masked: {HIGHLIGHT_GRAY_DARK_BG}T---{END}")
parser.add_argument("-v", "--verbose", action="store_true",
	help="Print an alignment to stdout, in addition to -ao if defined")
parser.add_argument("-bv", "--backmask_verbose", action="store_true",
	help="List all positions that get backmasked and print an alignment of backmasked diffs (no effect if not backmasking)")
parser.add_argument("-vv", "--veryverbose", action="store_true",
	help="Print an alignment to stdout, in addition to -ao if defined, even if masked/reference")
parser.add_argument("-pd", "--print_diffionaries", action="store_true",
	help="Print all diff files as they are interpreted as dictionaries (does not interact with -v nor -vv)")
args = parser.parse_args()

if args.veryverbose:
	args.verbose = True

if args.light and not args.colors:
	print("Warning: You used -l without -c. -; is only necessary if -c AND a black-background terminal. To enable highlights use -c too.")

BLACK = BLACK_DARK_BG if (args.light and args.colors) else BLACK_LIGHT_BG
HIGHLIGHT_CYAN = HIGHLIGHT_CYAN_DARK_BG if (args.light and args.colors) else HIGHLIGHT_CYAN_LIGHT_BG
HIGHLIGHT_GREEN = HIGHLIGHT_GREEN_DARK_BG if (args.light and args.colors) else HIGHLIGHT_GREEN_LIGHT_BG
HIGHLIGHT_GRAY =  HIGHLIGHT_GRAY_DARK_BG if (args.light and args.colors) else HIGHLIGHT_GRAY_LIGHT_BG

C_BLACK = BLACK if args.colors else ''
C_RED = RED if args.colors else ''
C_END = END if args.colors else ''
C_HIGHLIGHT_CYAN = HIGHLIGHT_CYAN if args.colors else ''
C_HIGHLIGHT_GREEN = HIGHLIGHT_GREEN if args.colors else ''
C_HIGHLIGHT_GRAY = HIGHLIGHT_GRAY if args.colors else ''
C_FADE = FADE if args.colors else ''

def printwrite_lines(lines: list, outfile: None | str, both=False) -> None:
	if both:
		for line in lines:
			print(line)
	if outfile is not None:
		with open(outfile, "w") as f:
			f.writelines(f"{line}\n" for line in lines)

def printwrite_summary(diffionaries, all_positions, incongruence):
	lines_to_print=[]
	lines_to_print.append('')
	for input_diff in diffionaries:
		lines_to_print.append(f"{input_diff.sample} has {len(input_diff.data)} non-reference SNPs and masked positions")
	lines_to_print.append(f"\nComparing across all diffs:\n{len(incongruence['incongruent_positions'])} out of {len(all_positions)} positions have at least one mismatch or mask.")
	lines_to_print.append(f"\t{len(incongruence['snp_incongrence_positions'])} positions are SNP mismatches (ref-SNP or SNP-SNP)")
	lines_to_print.append(f"\t{len(incongruence['masked_incongruence_positions'])} positions have a mask-nomask mismatch")
	lines_to_print.append(f"\t{len(incongruence['masked_total_positions']) - len(incongruence['masked_incongruence_positions'])} positions are masked across all samples")
	#lines_to_print.append("\nNoteworthy positions summary:")
	#lines_to_print.append(f"\t{masked_snps} positions of newly-masked SNPs")
	#lines_to_print.append(f"\t{incong_snps} positions of incongruent SNPs")
	#lines_to_print.append(f"\t{icg_ref_snp} positions of SNP-ref incongruence")
	printwrite_lines(lines_to_print, args.summary_outfile, both=True)


class Diff:
	"""Represents a diff file"""
	def __init__(self, path: str, sample: str, data: dict):
		self.path = path  # previously acted as the key in diffionaries
		self.sample = sample
		self.data = data
		# the data dictionary looks like this
		# {123: "A", 125: "T"}

	def print_all(self):
		print(f">{self.sample}")
		for positions, snps in self.data.items():
			print(f"{positions}\t{snps}\t1")

diffionaries = []

with open(args.input_file_with_diff_paths) as pile_of_diffs:
	diff_files = [line.strip("\n") for line in pile_of_diffs.readlines()]
	for line in diff_files:
		print(line)
	exit(999)

for diff_file in diff_files:
	with open(diff_file, "r") as input_diff:
		sample_name = input_diff.readline().strip().strip(">") # after this readline() we are now at the first (0th) SNP position
		diff_data = input_diff.readlines()                     # read all remaining (eg, all non-sample) lines

	keys = []
	values = []
	for line in diff_data:
		key = int(line.split()[1])     # position is unique, so they are the keys in the dictionary
		value = str(line.split()[0])   # SNP/mask
		repeat = int(line.split()[2])  # the third column in the diff tells us if the SNP/mask repeats
		if repeat != 1:
			for j in range(0, repeat):
				keys.append(key+j)
				values.append(value)
		else:
			keys.append(key)
			values.append(value)
	this_diff = Diff(diff_file, sample_name, {keys[i]: values[i] for i in range(len(keys))})
	diffionaries.append(this_diff)
print(f"Converted {len(diff_files)} diffs to dictionaries.")

if args.print_diffionaries: [diff.print_all() for diff in diffionaries]

all_positions = set()
for i, input_diff in enumerate(diffionaries):
	for position in input_diff.data:
		if position not in all_positions:
			all_positions.add(position)
all_positions = sorted(all_positions)
print(f"Processed {len(all_positions)} sites.")

# stores just position integers for all types of mismatch
incongruence = {'incongruent_positions': set(), 
				'snp_incongrence_positions': set(),     # eg, one sample is ref and another is C SNP, or one is G SNP and another is T SNP
				'masked_incongruence_positions': set(), # eg, one sample is G SNP and another is masked, or one is ref and another is masked
				'masked_total_positions': set()}        # masked_incongruence + positions where ALL samples get masked

# stores position + samples at that position as string for just noteworth mismatches
noteworthy = dict()

# alignment, which excludes ref-mask and full-mask positions unless args.veryverbose
alignment = list()

for position in tqdm(all_positions, disable=args.verbose):
	each_sample = []
	for input_diff in diffionaries:
		if position not in input_diff.data.keys():
			# this sample is missing information because it is ref
			each_sample.append(f"{C_RED}R{C_BLACK}")  # purposely not using END so the highlight continues
		else:
			each_sample.append(input_diff.data[position])
	samples_at_this_position = ''.join(sample for sample in each_sample)

	if "-" in samples_at_this_position:
		# This position is masked in AT LEAST ONE sample
		incongruence['incongruent_positions'].add(position)
		incongruence['masked_total_positions'].add(position)
		if ''.join(sample for sample in each_sample) != ''.join("-" for sample in each_sample):
			# This position is masked in at least one sample
			incongruence['masked_incongruence_positions'].add(position)
			if any(SNP in samples_at_this_position for SNP in ('A', 'T', 'G', 'C')):
				# Masking this position will mask a SNP
				position_and_samples = f"{C_HIGHLIGHT_GRAY}{str(position).zfill(7)}\t{''.join(sample for sample in each_sample)}{C_END}"
				noteworthy.update({str(position).zfill(7): [position_and_samples, "masked SNP"]})
				alignment.append(position_and_samples)
			else:
				# Masking this position will just mask one or more ref calls
				if args.veryverbose: alignment.append(f"{C_FADE}{str(position).zfill(7)}\t{''.join(sample for sample in each_sample)}{C_END}")
		else:
			# This position is masked in ALL samples (no incongruence)
			if args.veryverbose: alignment.append(f"{C_FADE}{str(position).zfill(7)}\t{''.join(sample for sample in each_sample)}{C_END}")
	
	elif samples_at_this_position.count(samples_at_this_position[0]) != len(samples_at_this_position):
		incongruence['incongruent_positions'].add(position)
		incongruence['snp_incongrence_positions'].add(position)
		if "R" not in samples_at_this_position:
			# Incongruent SNPs, with no samples being reference (ex: TTTA) -- this is rare!
			position_and_samples = f"{C_HIGHLIGHT_CYAN}{str(position).zfill(7)}\t{''.join(sample for sample in each_sample)}{C_END}"
			noteworthy.update({str(position).zfill(7): [position_and_samples, "incongruent SNPs"]})
		else:
			# At least one sample calls SNP and another calls reference, and no samples are masked
			position_and_samples = f"{C_HIGHLIGHT_GREEN}{str(position).zfill(7)}\t{''.join(sample for sample in each_sample)}{C_END}"
			noteworthy.update({str(position).zfill(7): [position_and_samples, "SNP-ref incongruence"]})
		alignment.append(f"{position_and_samples}")
		
	
	else:
		# All samples either ref or the same SNP
		alignment.append(f"{str(position).zfill(7)}\t{''.join(sample for sample in each_sample)}")

assert len(incongruence['masked_total_positions']) + len(incongruence['snp_incongrence_positions']) == len(incongruence['incongruent_positions'])

printwrite_lines(alignment, args.alignment_outfile, both=args.verbose)
printwrite_summary(diffionaries, all_positions, incongruence)

noteworthy_ordered = sorted(noteworthy)
masked_snps = 0
incong_snps = 0
icg_ref_snp = 0
for position in noteworthy_ordered:
	if noteworthy.get(position)[1] == "masked SNP":
		masked_snps += 1
	elif noteworthy.get(position)[1] == "incongruent SNPs":
		incong_snps += 1
	elif noteworthy.get(position)[1] == "SNP-ref incongruence":
		icg_ref_snp += 1
	else:
		raise ValueError(f"Unrecognized noteworthy alignment at {position}: {noteworthy.get(position)[1]}")

if len(diff_files) < 10:
	print("\nNoteworthy alignments:")
	for position in noteworthy_ordered:
		print(f"{noteworthy.get(position)[0]}\t{noteworthy.get(position)[1]}")
else:
	print("Not printing noteworthy alignments, since there's more than 10 diff files involved.")


if args.mask_outfile:
	with open(args.mask_outfile, "a") as f:
		for position in incongruence['masked_incongruence_positions']:
			f.write(f"N{position}N\n")
	print(f"\nWrote information about incongruence in masking to {args.mask_outfile}")

if args.backmask:
	backmasked_diffs = []
	for input_diff_object in diffionaries:
		print(f"Backmasking {input_diff_object.sample}...")
		backmasked_positions = []
		retained_positions = []
		output_data = {} # dict, not set
		for position in incongruence['masked_incongruence_positions']:
			if position not in input_diff_object.data.keys():
				if args.backmask_verbose: print(f"Masking reference call at position {position}")
				output_data[position] = "-"
				backmasked_positions.append(position)
			elif input_diff_object.data[position] != "-":
				if args.backmask_verbose: print(f"Masking {input_diff_object.data[position]} SNP at position {position}")
				output_data[position] = "-"
				backmasked_positions.append(position)
			else:
				if args.backmask_verbose: print(f"Leaving {input_diff_object.data[position]} in place at position {position}")
				output_data[position] = input_diff_object.data[position]
				retained_positions.append(position)
		for position in input_diff_object.data.keys():
			if position not in output_data:
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
		print(f"For {new_diff.sample}, backmasked {len(backmasked_positions)} positions.")
		#print(*backmasked_positions, end="\n\n")

	if args.verbose:
		print("New realignment of backmasked diffs:")
		for position in all_positions:
			each_sample = []
			for backmasked_diff in backmasked_diffs:
				if position not in backmasked_diff.data.keys():
					# this sample is missing information because it is ref
					each_sample.append(f"{C_RED}R{C_BLACK}")  # purposely not using END so the highlight continues
				else:
					each_sample.append(backmasked_diff.data[position])
			samples_at_this_position = ''.join(sample for sample in each_sample)
			print(f"{position}\t{samples_at_this_position}")
