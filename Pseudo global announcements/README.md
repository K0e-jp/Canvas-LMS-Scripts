## Notes


The 2 scripts have the same core function with different levels of complexity, I would suggest building on the standard version to customize to your desire.


### Standard_global_announcement


Posts the same announcement in every course in the given terms, the announcement gets posted as the admin user that owns the API token used. The message posted is customizable after line 60. there is also an example on how to include a hard coded link in the announcement (the link is static and remains the same in every course)


### Fancy_global_announcement


Final version for my usecase.

Adds a function to fetch data on who the primary instructor of each course is and makes sure the standard announcemet gets posted as the instructor for that course. I found this to be the best option if your institution doesn't use a "non-human" admin account to generate API tokens. 

This version also includes an example on how you can include a course-specific custom link for each announcement. The find_item_id function on line 55 finds the id of an item with a specific name (defined on line 68), this id then gets used in the main function to create a link to that item that gets included in the main text. This is handy if every course in your term has an item/module/page with the same name (for example a page with AI policies, an external tool item for course evaluations, etc.). The message posted is customizable after line 102.

