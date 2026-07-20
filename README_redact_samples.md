# redact_samples.py

Tree Nine users who are tracking clusters over time usually build a combined diff file over the course of multiple runs. It may come out that you have to redact some samples. This is the recommended redaction process, using [redact_samples.py](https://github.com/aofarrel/diffdiff/blob/main/redact_samples.py):

These instructions assume you're running Tree Nine in Terra but the same logic applies for non-Terra setups.

1. Download the most recent completed Tree Nine run's (heneforth "last run"):
	* combined diff file (bigtree_combinedYYYY-MM-DD.diff)
 	* samples added file (samples_added_YYYY-MM-DD)
    * ...as well as **set** data table from Terra's Data tab, which will be a zip (whatever_set.zip)
2. Create a denylist ONLY containing denylisted samples that are already present in your combined diff file/samples added file 
	* Recall that your combined diff file and your samples added file reference the exact same samples
	* If redacting samples that match a certain pattern, use your favorite regular expression doohickey (sed, perl, Sublime Text, etc) to pull out all lines matching that pattern from the samples_added file and save as denylist.txt
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
10. In Terra, delete the set data table, but NOT the sample-level data table
11. In Terra, upload your manually-modified `whatever_set/whatever_set_entity.tsv`, which now has those two updated paths to point to the MODIFIED combined diff and samples_added files, as a data table in the usual method
	* You can use FISS for this but for most users dragging-and-dropping into the UI is simpler (wait for the UI to show success in the top right, will take a minute or two)
12. In Terra, upload your modified `MODIFIED_whatever_set_membership.tsv` file
	* Terra will throw a warning saying the data table already exists, but this is okay
	* As with before wait for the UI to show a success
13. To finish redaction, run Tree Nine on a batch of brand new samples, **with `process_clusters.no_dropped_sample_failsafe` set to true**. Tree Nine will treat your redacted samples as if they are dropped samples (but they will not appear in the unclustered samples file). This run will take in:
	* Last run's **unmodified** cluster JSON, persistent META, and persistent IDs
    * Your MODIFIED combined diff file (`updated_diff_file`)
    * Your MODIFIED samples_added file (`updated_diff_contents`)
    * `process_clusters.no_dropped_sample_failsafe` = `true`
    * Everything else is like a normal Tree Nine run
   
> [!WARNING]  
> You should not attempt to redact the cluster JSON, the persistent cluster IDs file, nor the persistent cluster META file. It is unnecessary because running Tree Nine (see step 12) will create new versions of these files without the samples.<sup>†</sup> It is also quite likely to break things.
>
> If you ever end up in a scenario where you *absolutely must, for legal reasons,* redact *every* file, retaining *no previous versions* of older files, you must ensure:
> * you do not create one-sample clusters; if one is created, you must manually handle it as a decimated cluster
> * you properly handle parent clusters with decimated children
> * you handle all of the non-user-facing JSON fields (newly_decimated vs decimated, newly_updated, samples_previously, etc)...
> * you force *all* Microreact projects to update in step 12 via `process_clusters.force_microreact_update`, because a full redaction would prevent the pipeline from detecting the samples being dropped, ergo might not trigger Microreact updates, ergo might leave redacted samples up on Microreact
> 	* even though Microreact projects can be downloaded as .json files in the UI, there is no way to do that with the API, which means you (nor Tree Nine) cannot check Microreact project's contents with the API
>   * note that `process_clusters.force_microreact_update` might force Microreact projects of existing decimated clusters to no longer list what samples were in that cluster prior to decimation, as that relies on the "sample_id_previously" field which is cleared every run (to avoid creating hugely massive JSONs)


<sup>†</sup>The cluster JSON holds onto the names of samples previously in the cluster, so old sample names will be mentioned in the "sample_id_previously" field of the JSON you generate via Tree Nine (step 12). However, if you do an additional run after that, all trace will be removed, because "sample_id_previously" only goes back to the previous run.
