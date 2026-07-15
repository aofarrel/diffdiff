# redact_samples.py

Tree Nine users who are tracking clusters over time usually build a combined diff file over the course of multiple runs. It may come out that you have to redact some samples. This is the recommended redaction process, using [redact_samples.py](https://github.com/aofarrel/diffdiff/blob/main/redact_samples.py):

These instructions assume you're running Tree Nine in Terra but the same logic applies for non-Terra setups.

1. Download the most recent completed Tree Nine run's (heneforth "last run"):
	* combined diff file (bigtree_combinedYYYY-MM-DD.diff)
 	* samples added file (samples_added_YYYY-MM-DD)
    * ...as well as **set** data table, which will be a zip (whatever_set.zip)
2. Create a denylist ONLY containing denylisted samples that are already present in your combined diff file/samples added file (recall that both files reference the same samples)
	* The easiest way to do this if you are redacting samples that match a certain pattern: Use your favorite regular expression doohickey (sed, perl, Sublime Text, etc) to pull out all lines matching that pattern from the samples_added file and save as denylist.txt
	* If you choose not to do this and instead use a denylist that includes samples not in the combined diff file, the next step will throw an error to prevent footguns. You can suppress that error with `--looseygoosey` but this is not recommended.
4. `python3 redact_samples.py denylist.txt --samples_added_file samples_added_YYYY-MM-DD --combined_diff_file bigtree_combined_YYYY-MM-DD.diff`
5. Unzip whatever_set.zip to get whatever_set/whatever_set_membership.tsv and whatever_set/whatever_set_entity.tsv, but keep the zip too
6. Create a denylist containing ALL denylisted samples present in your set data table. If your set data table includes multiple instances of a denylisted sample, your denylist should contain the same number of instances (order doesn't matter). 
	* Easiest way to to this if: Use your favorite regular expression doohickey to pull out all samples matching the pattern from `whatever_set/whatever_set_membership.tsv`'s second column and save as denylist_complete.txt
	* As with #2 you technically *can* use a generic denylist where (n samples denylist != n samples to remove from data table), if you run the next step with `--looseygoosey`, but it's not recommended
7. `python3 redact_samples.py denylist_complete.txt --set_data_table_zip whatever_set.zip`
8. You will now have three MODIFIED files which you should upload to a Terra workspace bucket:  
	a) MODIFIED_bigtree_combined_YYYY-MM-DD.diff  
	b) MODIFIED_samples_added_YYYY-MM-DD  
	c) MODIFIED_whatever_set_membership.tsv  
9. Go to your unzipped set table's **unmodified** `whatever_set/whatever_set_entity.tsv` file and edit the most recent completed Tree Nine run's values for updated_diff_file **and** updated_diff_contents to point to their respective MODIFIED files.
	* Example: In the set table, the most recent completed Tree Nine run has the value `gs://fc-bucketname/submissions/submission_id/Tree_Nine/workflow_id/call-cat_diff_files/glob_id/samples_added_2026-06-14` for updated_diff_contents (ie, that was a workflow-level output). You could replace that with `gs://fc-bucketname/redacted_versions/MODIFIED_samples_added_2026-06-14`, then repeat for updated_diff_file.
	* Do not worry about the cluster JSON, persistent META file, or persistent ID files. They will retain traces of your redacted samples, but they are not user-facing, and for a variety of reasons it is a bad idea to attempt to redact them too.
10. In Terra, delete the bucketname data table, but NOT the sample-level whatever data table
11. In Terra, upload your manually-modified `whatever_set/whatever_set_entity.tsv`, which now has those two updated paths to point to the MODIFIED combined diff and samples_added files, as a data table in the usual method
	* You can use FISS for this but for most users dragging-and-dropping into the UI is simpler (wait for the UI to show success in the top right, will take a minute or two)
12. In Terra, upload your modified `MODIFIED_whatever_set_membership.tsv` file
	* Terra will throw a warning saying the data table already exists, but this is okay
	* As with before wait for the UI to show a success
13. Run Tree Nine on a new batch of samples as usual. Your redacted samples will be considered dropped samples.
