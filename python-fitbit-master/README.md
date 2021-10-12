# Proposal

## What will (likely) be the title of your project?

Fitbit HR Data Extraction

## In just a sentence or two, summarize your project. (E.g., "A website that lets you buy and sell stocks.")

A website which can access fitbit data for patients enrolled in my lab study.

## In a paragraph or more, detail your project. What will your software do? What features will it have? How will it be executed?

I work for a lab at the Yale PET center, and we are starting a study on the effects of exercise and Parkinson's disease progression.
We will be having our patients wear fitbits for 6 months in order to track their activity, and we need a way for us to retrieve their data.
My idea is to create a web interface which will use Fitbit's API to call user data, have the ability to download it to our local drives,
store portions in an SQL database inorder to do graphical comparisons, and notify patients which are not fulfilling exercise requirements via email.
My intention is to host the site on my github and use FLASK for the majority of the programming.

## If planning to combine CS50's final project with another course's final project, with which other course? And which aspect(s) of your proposed project would relate to CS50, and which aspect(s) would relate to the other course?

TODO, if applicable

## If planning to collaborate with 1 or 2 classmates for the final project, list their names, email addresses, and the names of their assigned TFs below.

TODO, if applicable

## In the world of software, most everything takes longer to implement than you expect. And so it's not uncommon to accomplish less in a fixed amount of time than you hope.

### In a sentence (or list of features), define a GOOD outcome for your final project. I.e., what WILL you accomplish no matter what?

Good outcome:
-able to download data to local drive with minimal patient and researcher input
-have an active site (password protected) to facilitate this process

essential:
-program which downloads data from the fitbit cloud in an automated fashion (once a day)

### In a sentence (or list of features), define a BETTER outcome for your final project. I.e., what do you THINK you can accomplish before the final project's deadline?

-have some sort of graphical interphase with which our less tech-savy lab members can interact with
-have a flagging mechanism which sends emails to patients who are not fulfilling our requirements

### In a sentence (or list of features), define a BEST outcome for your final project. I.e., what do you HOPE to accomplish before the final project's deadline?

-incorporate other collection devices we are using in the lab (heart ratre straps and ECG) into the site
-compare readings of new collections to the Fitbit data
-add other statistical functionality to the graph data

## In a paragraph or more, outline your next steps. What new skills will you need to acquire? What topics will you need to research? If working with one of two classmates, who will do what?

I need to research how to work with the Fitbit API and call data. I also need to see if there are any libraries I can import in order to make this process easier.
For that, I will try to check stackexchange to see if anyone has done this previously. I also need to see how to download data to a local drive and what paths I need to establish in order to do so.
I will also need to investigate if there is a way for that process to happen automatically. Additionally, I need to see how to incorporate graphs in a webpage. I think there is a matlab
library which can help me with that, but I still need to look into that.
