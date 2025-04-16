## Notes


The script was originally created to add an Anthology Course Evaluation (external tool) item in every course active in a given semester, but can be adapted to fit different external tools.


### Variables that need to be edited other than lines 4/5/6:


- Line 47 | Name of the new module to be created
- Line 74 | Title of the new item to be created
- Line 121 | Redirect URL for the external tool


### Additional edits:


On line 49 and 79 publishing the module/item in the main payload doesn't seem to be working (left as commented), the sections after line 61 and 91 (#publish) send a second request to publish them after they are created, delete or comment those lines if you wish for the items/modules to stay unpublished.


unhide_modules_tab function on line 98 sends a request to make sure the modules tab is visible for users on the left menu of the course (if the modules tab was manually hidden by the instructor pubslishing something in it won't unhide it). Don't run this function on line 130 if you don't want this to happen.



