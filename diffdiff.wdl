version 1.0

# Two seperate tasks for diffdiff to avoid having to deal with the headache
# of WDL's handling of optional files in downstream tasks.

task diffdiff_usher_mask {
    input {
        Array[File] diffs
    }
    command <<<
    wget https://raw.githubusercontent.com/aofarrel/diffdiff/main/diffdiff.py
    
    echo "~{sep='\n' diffs}" >> diff_paths.txt
    
    python3 diffdiff.py diff_paths.txt -mo usher_mask.tsv
    
    >>>
    runtime {
		cpu: 4
		disks: "local-disk " + 10 + " HDD"
		docker: "ashedpotatoes/sranwrp:1.1.15"
		memory: "8 GB"
		preemptible: 2
	}
    output {
        File usher_mask = "usher_mask.tsv"
        #Array[File] backmasked_diffs = glob("*.backmask.diff")
    }
}

task diffdiff_backmask {
    input {
        Array[File] diffs
    }
    command <<<
    wget https://raw.githubusercontent.com/aofarrel/diffdiff/main/diffdiff.py
    
    echo "~{sep='\n' diffs}" >> diff_paths.txt
    
    python3 diffdiff.py diff_paths.txt -b
    
    >>>
    runtime {
		cpu: 4
		disks: "local-disk " + 10 + " HDD"
		docker: "ashedpotatoes/sranwrp:1.1.15"
		memory: "8 GB"
		preemptible: 2
	}
    output {
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

}