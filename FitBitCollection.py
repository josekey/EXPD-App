# libraries for API
import fitbit 
import gather_keys_oauth2 as Oauth2
import pandas as pd 
import datetime


def main():
    # file path to FitBitData folder
    p = 'C:/Users/Jose/Box/FitBitData'

    patients = pd.read_csv(f'{p}/Patients.csv')
    df_old = pd.read_csv(f'{p}/FitBitData.csv')

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

    # loop through active subjects and create clients
    for index, row in patients.iterrows():
        input(f'\nLog into FitBit with...\n Username: {row["username"]}\n Password: {row["password"]}')
        auth2_client = set_client(row)
        
        #getting single day data into list of df
        for oneDate in allDates:
            #oneDate = oneDate.date().strtime('%Y-%m-%d')
            oneDayData = auth2_client.intraday_time_series('activities/heart', base_date = oneDate, detail_level= '1sec')
            df = pd.DataFrame(oneDayData['activities-heart-intraday']['dataset'])
            name =  [row["Participant"] for i in range(len(df.index))]
            df["Participant"] = name
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
    final_df.sort_values(by = ['Participant','date','time'])

    final_df.to_csv(f'{p}/FitBitData.csv', index = False)
      
# creating OAuth2 user for pushes and calls  
def set_client(row):
    #bringing in global variable into function 

    CLIENT_ID = row['client_id']
    CLIENT_SECRET= row['secret']

    print(CLIENT_ID)
    print(CLIENT_SECRET)

    # setting call and collecting access token --> make into helper function 
    server=Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
    server.browser_authorize()
    ACCESS_TOKEN=str(server.fitbit.client.session.token['access_token'])
    REFRESH_TOKEN=str(server.fitbit.client.session.token['refresh_token'])

    return fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET,oauth2=True,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)


  
if __name__ == '__main__':
    main()