# diffdiff
 Highlight the differences between MAPLE-formatted genomic diff files by aligning them by position. Can display just SNP-ref, SNP-SNP, and SNP-mask differences, or show literally *every* difference. Output full alignment, noteworthy-only alignment, `matUtils mask`-ready input, and summary information to a file. Use ANSI highlighting -- or not -- to make differences really stand out in the terminal.
 
 Use cases:
 * You have a small number (ideally less than 100) highly-clonal sequences and want to look at every difference between them
 * You want to validate phylogenetic analysis/distance matrices between samples
 * You want to run matUtils mask
 * You want to backmask (see -h) some diff files, are aware of the limitations, and cannot/do not wish to use Tree Nine's method of backmasking

 diffdiff is not a replacement for phylogenetics software. Please consider using UShER instead if you have more than 100 samples.
 
 ## What are MAPLE diff files?
 Essentially VCFs but with much less detail, see /tests/ for examples. Everything is represented as either a SNP or an explict mask (`-`). First column is allele, second is position, third is how long the allele is. Example: `A 123 2` means that at positions 123 and 124, non-reference SNP `A` is called.

 You can generate MAPLE diff files using VCF-to-diff generators. The myco pipeline goes all the way from FASTQs (or BioSample accessions) and outputs MAPLE diff files at the end.