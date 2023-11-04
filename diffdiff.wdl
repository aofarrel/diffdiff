version 1.0

task diffdiff {
    input {
        Array[File] diffs
        Boolean backmask = true
    }
    command <<<
    wget https://raw.githubusercontent.com/aofarrel/diffdiff/main/diffdiff.py
    
    # find every file in diffs and write their address to a text file, then pass that into diffdiff.py
    
    python diffdiff.py diff_paths.txt ~{backmask} alignment.txt # TODO: does python need capital T True here
    
    >>>
    runtime {
		cpu: 4
		disks: "local-disk " + 10 + " HDD"
		docker: "ashedpotatoes/sranwrp:1.1.15"
		memory: "8 GB"
		preemptible: 2
	}
    output {
        File alignment = "alignment.txt"
        Array[File] backmasked_diffs = glob("*.backmask.diff")
    }
}