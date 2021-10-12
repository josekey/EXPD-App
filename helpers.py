# libraries for API
import fitbit 
import gather_keys_oauth2 as Oauth2
import pandas as pd 
import datetime
import csv

# libraries for webdev
from flask import redirect, render_template, request, session, flash
from functools import wraps

# check if connected 
connected = False

# ensures client is linked in order for data extraction 
def client_required():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not(connected):
                flash('Must be connected to FitBit to perform this function','error')
                return redirect("/connect")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# linking with FitBit API for specific patient
def set_client(row):
    # getting passes id and secret
    CLIENT_ID = row['client_id']
    CLIENT_SECRET= row['secret']

    # setting call and collecting access token 
    server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
    server.browser_authorize()
    ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
    REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])

    # making client
    auth2_client = fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET,oauth2=True,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)
    global connected
    connected = True

    return auth2_client

# getting pandas dataframe with HR data
def get_df(d1, d2, auth2_client):
    # changing from string to datetime
    d1 = d1.split('-')
    d1 = datetime.datetime(int(d1[0]), int(d1[1]), int(d1[2]))
    
    d2 = d2.split('-')
    d2 = datetime.datetime(int(d2[0]), int(d2[1]), int(d2[2]))

    # allocating variables for data retreival
    date_list = []
    df_list = []
    allDates = pd.date_range(start = d1, end = d2)
  
    #getting single day data into list of df
    for oneDate in allDates:
        print(oneDate)
        oneDayData = auth2_client.intraday_time_series('activities/heart', base_date = oneDate, detail_level= '1sec')
        try:
            df = pd.DataFrame(oneDayData['activities-heart-intraday']['dataset'])
        except:
            return None
        date_list.append(oneDate)
        df_list.append(df)
  
    #stitching together all the dataframes
    final_df_list = []
    for date, df in zip(date_list, df_list):
        if len(df) == 0:
            continue
        df.loc[:, 'date'] = pd.to_datetime(date)
        final_df_list.append(df)
    if len(final_df_list) == 0:
        return None
    final_df = pd.concat(final_df_list, axis  = 0)
    return final_df

# update csv with new participant
def add_participant(entry):
    # checking to see if entry conflicts with existing subjects
    with open('patients.csv', "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if entry['id'] == row['id']:
                return 1
            if entry['client_id'] == row['client_id']:
                return 2
    
    ### '''todo''' try to connect to api

    # append new row into csv
    with open('patients.csv', "a", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id','client_id','secret'] )
        writer.writerow(entry)

    return 0

# returns list of dictionaries with patient OAuth2.0 info
def update_patients():
    patients = []
    with open('patients.csv', "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            patients.append(row)
    return patients


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code