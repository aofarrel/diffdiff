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
        Boolean ANSI_colors = false

        # alternative color palettes, no ops if ANSI_colors = false
        Boolean dark_background = false
        Boolean deuteranopia = false
    }
    command <<<
    wget 
    
    echo "~{sep='\n' diffs}" >> diff_paths.txt

    if [[ "~{ANSI_colors}" == "true" ]]
    then
        python3 /scripts/diffdiff.py diff_paths.txt \
            -ao full_alignment.txt \
            -no noteworthy_alignment.txt \
            -mo usher_mask.tsv \
            ~{if dark_background then "--altcolors" else "--colors"} ~{if deuteranopia then "--deuteranopia" else ""}
    else
        python3 /scripts/diffdiff.py diff_paths.txt -ao full_alignment.txt -no noteworthy_alignment.txt -mo usher_mask.tsv
    fi
    
    >>>
    runtime {
		cpu: 4
		disks: "local-disk " + 10 + " HDD"
		docker: "ashedpotatoes/sranwrp:1.3.1"  # contains diffdiff.py version 0.2.1
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
        Boolean ANSI_colors = false

        # alternative color palettes, no ops if ANSI_colors = false
        Boolean dark_background = false
        Boolean deuteranopia = false
    }
    command <<<
    set -eux pipefail
    
    DIFFS=( ~{sep=' ' diffs} )
    for FILE in "${DIFFS[@]}"
    do
       mv "$FILE" .
    done
    
    find . -name "*.diff" >> diff_paths.txt
    if [[ "~{ANSI_colors}" == "true" ]]
    then
        python3 /scripts/diffdiff.py diff_paths.txt \
            -ao full_alignment.txt \
            -no noteworthy_alignment.txt \
            -b \
            -c ~{if dark_background then "--altcolors" else ""} ~{if deuteranopia then "--deuteranopia" else ""}
    else
        python3 /scripts/diffdiff.py diff_paths.txt -ao full_alignment.txt -no noteworthy_alignment.txt -b
    fi
    
    >>>
    runtime {
		cpu: 4
		disks: "local-disk " + 10 + " HDD"
		docker: "ashedpotatoes/sranwrp:1.3.0"  # contains diffdiff.py version 0.2.1
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
        File full_alignment = select_first([diffdiff_backmask.full_alignment, diffdiff_usher_mask.full_alignment])
        File noteworthy_positions_alignment = select_first([diffdiff_backmask.noteworthy_alignment, diffdiff_usher_mask.noteworthy_alignment])
        File? usher_mask = diffdiff_usher_mask.usher_mask
        Array[File]? backmasked_diffs = diffdiff_backmask.backmasked_diffs
    }

}
