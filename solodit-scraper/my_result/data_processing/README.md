The result from running the websraper can be seen in results.json

To remove all duplicates, duplicate_remover was run with results.json and gave no_duplicates.json and duplicates.json as output.
no_duplicates.json is results.json with no duplicates, duplicates.json includes all audit links that were present in multiple search categories.

In order to know which links were found as duplicates, mark_duplicates.json was run with duplicates.json and no_duplicates.json, and gave in_scope.json as an output. Which are the in_scope audits for this thesis project.



To run the python scripts, you can write in terminal:

    python FILE_TO_RUN.py ARG_FILE1.json ARG_FILE2.json ARG_FILE3.json

Where FILE_TO_RUN.py is the file you want to run, and ARG_FILE is the files you want as arguments for the running function.