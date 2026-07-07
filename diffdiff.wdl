version 1.0

#
# Originally written for Tree Nine, this WDL is now a simple standalone wrapper for 
# the Python program. Most users would likely prefer to use the Python program.
#
# If backmasking, must be run with --copy-input-files on miniwdl
#

task diffdiff_usher_mask {
    input {
        Array[File] diffs
    }
    command <<<
    wget https://raw.githubusercontent.com/aofarrel/diffdiff/0.1.0/diffdiff.py
    
    echo "~{sep='\n' diffs}" >> diff_paths.txt
    
    python3 diffdiff.py diff_paths.txt -ao full_alignment.txt -no noteworthy_alignment.txt -mo usher_mask.tsv
    
    >>>
    runtime {
		cpu: 4
		disks: "local-disk " + 10 + " HDD"
		docker: "ashedpotatoes/sranwrp:1.1.15"
		memory: "8 GB"
		preemptible: 2
	}
    output {
        File full_alignment = "full_alignment.txt"
        File noteworthy_alignment = "noteworthy_alignment.txt"
        File usher_mask = "usher_mask.tsv"
    }
}

task diffdiff_backmask {
    input {
        Array[File] diffs
    }
    command <<<
    set -eux pipefail
    wget https://raw.githubusercontent.com/aofarrel/diffdiff/0.1.0/diffdiff.py
    
    DIFFS=( ~{sep=' ' diffs} )
    for FILE in "${DIFFS[@]}"
    do
       mv "$FILE" .
    done
    
    find . -name "*.diff" >> diff_paths.txt
    
    python3 diffdiff.py diff_paths.txt -ao full_alignment.txt -no noteworthy_alignment.txt -b
    
    >>>
    runtime {
		cpu: 4
		disks: "local-disk " + 10 + " HDD"
		docker: "ashedpotatoes/sranwrp:1.1.15"
		memory: "8 GB"
		preemptible: 2
	}
    output {
        File full_alignment = "full_alignment.txt"
        File noteworthy_alignment = "noteworthy_alignment.txt"
        Array[File] backmasked_diffs = glob("*.backmask.diff")
    }
}

workflow DiffDiff {
    input {
        Array[File] diffs   
        Boolean backmask = false
    }
    
    if(backmask) {
        call diffdiff_backmask {
            input:
                diffs = diffs
        }
    }
    
    if(!backmask) {
        call diffdiff_usher_mask {
            input:
                diffs = diffs
        }
    }

    output {
        File? full_alignment = select_first([diffdiff_backmask.full_alignment, diffdiff_usher_mask.full_alignment])
        File? noteworthy_positions_alignment = select_first([diffdiff_backmask.noteworthy_alignment, diffdiff_usher_mask.noteworthy_alignment])
        File? usher_mask = diffdiff_usher_mask.usher_mask
        Array[File]? backmasked_diffs = diffdiff_backmask.backmasked_diffs
    }

}
