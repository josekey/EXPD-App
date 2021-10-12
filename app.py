# libraries to work with data
import fitbit 
import gather_keys_oauth2 as Oauth2
import pandas as pd 
import numpy as np
import datetime

# web app libraries
from flask import Flask, flash, jsonify, redirect, render_template, request, session

## error catching and security
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

# imports helper functions
from helpers import apology, set_client, get_df, add_participant, update_patients, client_required

# Configure application
app = Flask(__name__)
app.secret_key='hello'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# setting global variables for client, active patient, patient FitBit info, and data frame
auth2_client = None
df = None
actsubj = None
patients = update_patients()

### beginning of app routes ###

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method =="POST":
        return 'TODO'
    else:
        return render_template("home.html")

# sets client through OAuth2.0 --> establish link with FitBit
@app.route("/connect", methods=["GET","POST"])
def connect():
    if request.method == "POST":
        # setting variables
        ## enable editing of global variables
        global auth2_client
        global actsubj
        subject = int(request.form.get('subject'))

        # setting up client for specific subj id
        for row in patients:
            if subject == int(row['id']):
                auth2_client = set_client(row)
                actsubj = subject

        # alert success and return
        flash('Subject '+str(actsubj)+' Connected', 'info')
        return redirect('/')
    else:
        # passing active patient ids to template for 'select'
        ids = []
        for row in patients:
            ids.append(row['id'])
        return render_template("connect.html", ids=ids)

# extract data and put into data frame
@app.route("/pull", methods=["GET","POST"])
@client_required()
def pull():
    if request.method == "POST":
        # form dataframe
        global df
        start = request.form.get("Start")
        end = request.form.get("End")
        df = get_df(start, end, auth2_client)

        # check to see if DF is empty
        print(str(type(df)))
        if df is None:
            flash('No Data Available for Selected Range', 'error')
            return redirect('/pull')

        #turn df into array to pass into google graph
        temp = df.loc[:, ['time','value']].to_numpy()
        df_list = [['Time', 'HR']]
        temp = temp.tolist()
        for item in temp:
            df_list.append(item)

        return render_template("display.html", df_list=df_list, d1=start, d2=end, id=actsubj)
    else:
        return render_template("data_request.html")

#download data 
@app.route("/download", methods=["POST"])
def download():
    df.to_csv('output/patient'+str(actsubj)+'_'+str(df.iloc[0]['date']).split(' ')[0] +'_'+ str(df.iloc[len(df)-1]['date']).split(' ')[0]+'.csv', index = False)
    flash('Download Successful', 'info')
    return redirect('/')

# register new participant
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # collect form data into dictionary
        new_entry = {'id': request.form.get('id'),
                    'client_id': request.form.get('client_id'),
                    'secret': request.form.get('secret')
                    }
        # collects code from function 
        ## function itself tries to add into csv
        passed = add_participant(new_entry)
        if not(passed):
            global patients
            patients = update_patients()
            flash("Participant Successfully Registered", 'info')
            return redirect('/')
        elif passed == 1:
            flash("Subject ID Already Exists",'error')
        elif passed == 2:
            flash("Client ID Already Registered",'error')
        return render_template('register.html')
    else:
        return render_template('register.html')

@app.route("/info", methods=["GET"])
def info():
    return render_template('info.html')

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)