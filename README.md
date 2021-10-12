# Welcome to the EXPD Web App
EXPD is the shorthand the Tinaz-Evans group uses to refer to their current study: finding correlation between patient exercise and Parkinson's Disease progression. In this study, we will be using FitBits to monitor patient heart rate in order to confirm their exercise is reaching optimal intensity for clinical observation (85% of max heart rate). The purpose of this app is to extract, view, and download the heart rate data from FitBit. 
## Installation 
Because this app runs locally, it is neccessary for the user to have an environment from which to run the app. In my case, I used a linux virutual machine with Visual Studio, which allowed me to create a virtual environment to house libraries required by the application. 
To install this particular framework, click [here](https://docs.microsoft.com/en-us/windows/python/web-frameworks), though many others should work. 

Next, we must install the appropriate libraries using the following command in the terminal of your interpreter/ ide. 
>>> pip3 install {{desired library}}
For example, in the case of installing pandas, we would say...
>>> pip3 install pandas

Here is the list of required libraries:
1. pandas
2. datetime
3. fitbit
4. cherrypy
5. flask
6. numpy

Now we must install the libraries that are downloaded locally in the EXPD folder. First navigate to the python-fitbit-master directory within the EXPD project, and then run the following command:
>>> python3 setup.py install

**The application is now set up.**

## Use
To run the application, ensure your current directory is EXPD, and run the following command in your terminal window:
>>> flask run

A webpage will then open, and you will be in the EXPD homepage! There should be a large picture of a colorful brain. 

Now, navigate to the Info tab by clicking on the link in the top right-hand corner of the page. This page has instructions to retrieve your client id and client secret from fitbit, as well as inputting them into the application and extracting data. 


[Youtube Tutorial](https://youtu.be/O_KddD74cHk)