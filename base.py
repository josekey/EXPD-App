# libraries for API
import fitbit 
import gather_keys_oauth2 as Oauth2
import pandas as pd 
import datetime

# setting global variable for client
auth2_client = None

#{'id': 1, 'client_id': '22C3DJ', 'secret': 'dc8470b473b3938e1fc3b4eec55350fc'}
# patient dataframe (patient_id, client_id, secret) 
## You will need to put in your own CLIENT_ID and CLIENT_SECRET
patients = [{'id': 2, 'client_id': '22BY6Z', 'secret': 'a79bda29129236da3dbaea11dcfe2ac9'},
            {'id': 1, 'client_id': '22C7YX', 'secret': '9ae5e4d1bafe9050e8323703814cf71f'}]

def main():
  global patients

  #specifying patient and setting client
  patient_id = None
  while not patient_id:
    patient_id = int(input('Enter patient id: '))
    for row in patients:
      print(patient_id, type(patient_id))
      print(row["id"])
      if row["id"] == patient_id:
        set_client(row)
        break
      
  #one day or multiple day range?
  range_choice = -1
  while range_choice != 0 and range_choice != 1:
    range_choice = int(input('One day(0) or date range(1)? '))
  if range_choice:
    range_data()
  else:
    day_data()
    
      
# creating OAuth2 user for pushes and calls  
def set_client(row):
  #bringing in global variable into function 
  global auth2_client

  CLIENT_ID = row['client_id']
  CLIENT_SECRET= row['secret']

  print(CLIENT_ID)
  print(CLIENT_SECRET)

  # setting call and collecting access token --> make into helper function 
  server=Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
  server.browser_authorize()
  ACCESS_TOKEN=str(server.fitbit.client.session.token['access_token'])
  REFRESH_TOKEN=str(server.fitbit.client.session.token['refresh_token'])

  auth2_client = fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET,oauth2=True,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)

def range_data():
  # getting dates
  d1 = None
  d2 = None
  while not d1:
    date_string = input('Start date (YYYY/MM/DD): ')
    temp = date_string.split('/')
    d1 = datetime.datetime(int(temp[0]), int(temp[1]), int(temp[2]))
  
  while not d2:
    date_string = input('End date (YYYY/MM/DD): ')
    temp = date_string.split('/')
    d2 = datetime.datetime(int(temp[0]), int(temp[1]), int(temp[2]))
    #end date must be after start
    td = d2-d1
    if td.days > 0:
      break
    else:
      d2 = None
  
  date_list = []
  df_list = []
  allDates = pd.date_range(start = d1, end = d2)
  
  #getting single day data into list of df
  for oneDate in allDates:
    #oneDate = oneDate.date().strtime('%Y-%m-%d')
    print(oneDate)
    oneDayData = auth2_client.intraday_time_series('activities/heart', base_date = oneDate, detail_level= '1sec')
    df = pd.DataFrame(oneDayData['activities-heart-intraday']['dataset'])
    date_list.append(oneDate)
    df_list.append(df)
  
  #stitching together all the dataframes
  final_df_list = []
  for date, df in zip(date_list, df_list):
    if len(df) == 0:
      continue
    df.loc[:, 'date'] = pd.to_datetime(date)
    final_df_list.append(df)
  final_df = pd.concat(final_df_list, axis  = 0)

  export_data(final_df)


# getting one day of data
def day_data():
  ##oneDate = pd.datetime(year = 2019, month = 10, day = 21)
  day = None
  while not day:
    date_string = input('Start date (YYYY/MM/DD): ')
    temp = date_string.split('/')
    day = datetime.datetime(int(temp[0]), int(temp[1]), int(temp[2]))
  oneDayData = auth2_client.intraday_time_series('activities/heart', day, detail_level='1sec')

  ## adding header to dataframe
  df = pd.DataFrame(oneDayData['activities-heart-intraday']['dataset'])
  df.head()

  export_data(df)

def export_data(df):
  # Export file to csv
  filename = input('Filename: ')
  df.to_csv(filename + '.csv', index = False)
  
if __name__ == '__main__':
  main()