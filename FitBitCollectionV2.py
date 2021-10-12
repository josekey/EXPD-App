# libraries for API
import fitbit 
import gather_keys_oauth2 as Oauth2
import pandas as pd 
import datetime


def main():
    # file path to FitBitData folder
    p = 'C:/Users/Jose/Box/FitBitData'

    patients = pd.read_csv(f'{p}/Patients.csv')
    old_hr = pd.read_csv(f'{p}/FitBit_HR.csv')
    old_sleep = pd.read_csv(f'{p}/FitBit_Sleep.csv')
    old_step = pd.read_csv(f'{p}/FitBit_Steps.csv')
    old_step_sum = pd.read_csv(f'{p}/FitBit_Steps_Summary.csv')
    
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

    # get all dates between start and end (inclusive)
    dates = pd.date_range(start = d1, end = d2)

    # initialize HR, sleep, and step count list
    hr = [old_hr]
    nap = [old_sleep]
    step_sum = [old_step_sum]
    step = [old_step]

    # loop through active subjects and create clients
    for index, row in patients.iterrows():
        if not row["username"]:
            break
        input(f'\nLog into FitBit with...\n Username: {row["username"]}\n Password: {row["password"]}')
        auth2_client = set_client(row)
        subj = row['Participant']
        
        # get data for subject into dataframe
        step_sum.append(steps_summary(auth2_client, dates, subj, p, old_step_sum))
        step.append(get_steps(auth2_client, dates, subj, p, old_step))
        hr.append(heart_rate(auth2_client, dates, subj, p, old_hr))
        nap.append(sleep(auth2_client, dates, subj, p, old_sleep))


    # removing None values from already counted dates
    step_sum = [i for i in step_sum if not i.empty]
    step = [i for i in step if not i.empty]
    hr = [i for i in hr if not i.empty]
    nap = [i for i in nap if not i.empty]

    #stitching together all the dataframes && double check for duplicates
    final_hr = pd.concat(hr)
    final_hr.drop_duplicates(subset=None, keep="first", inplace=True)
    final_hr = final_hr.sort_values(by = ['Participant','Date','Time'])

    final_nap = pd.concat(nap)
    final_nap.drop_duplicates(subset=None, keep="first", inplace=True)
    final_nap = final_nap.sort_values(by = ['Participant','Date'])

    final_step = pd.concat(step)
    final_step.drop_duplicates(subset=None, keep="first", inplace=True)
    final_step = final_step.sort_values(by = ['Participant','Date','Time'])

    final_step_sum = pd.concat(step_sum)
    final_step_sum.drop_duplicates(subset=None, keep="first", inplace=True)
    final_step_sum = final_step_sum.sort_values(by = ['Participant','Date'])
    

    # export
    try:
        final_hr.to_csv(f'{p}/FitBit_HR.csv', index = False)
        final_nap.to_csv(f'{p}/FitBit_Sleep.csv', index = False)
        final_step.to_csv(f'{p}/FitBit_Steps.csv', index = False)
        final_step_sum.to_csv(f'{p}/FitBit_Steps_Summary.csv', index = False)
    except PermissionError:
        print('Close csv files before running again.')
        quit()
    

    
def sleep(auth2_client, dates, subj, p, past):
    # getting list of dataframes for sleep data
    sleep_list = []
    for d in dates:
        if str(d)[:10] in past.loc[past['Participant'] == subj, 'Date'].tolist():
            print(f'Sleep for {subj} on {str(d)[:10]} already counted')
            continue
        try:
            fit_statsSum = auth2_client.sleep(date=d)['sleep'][0]
            ssummarydf = pd.DataFrame({'Participant':subj,
                        'Date':fit_statsSum['dateOfSleep'],
                        'MainSleep':fit_statsSum['isMainSleep'],
                        'Efficiency':fit_statsSum['efficiency'],
                        'Duration':fit_statsSum['duration'],
                        'Minutes Asleep':fit_statsSum['minutesAsleep'],
                        'Minutes Awake':fit_statsSum['minutesAwake'],
                        'Awakenings':fit_statsSum['awakeCount'],
                        'Restless Count':fit_statsSum['restlessCount'],
                        'Restless Duration':fit_statsSum['restlessDuration'],
                        'Time in Bed':fit_statsSum['timeInBed']
                                    } ,index=[0])
            sleep_list.append(ssummarydf)
        except IndexError:
            print(f'No sleep data for {subj} on {d}')

    if len(sleep_list) > 0:
        #stitching together all the dataframes
        final_df = pd.concat(sleep_list)
        final_df.sort_values(by = ['Participant','Date'])

        return final_df
    else:
        return pd.DataFrame()

def heart_rate(auth2_client, dates, subj, p, past):
    df_list = []
    for oneDate in dates:
        if str(oneDate)[:10] in past.loc[past['Participant'] == subj, 'Date'].tolist():
            print(f'HR for {subj} on {str(oneDate)[:10]} already counted')
            continue
        try:
            oneDayData = auth2_client.intraday_time_series('activities/heart', base_date = oneDate, detail_level= '1sec')
            df = pd.DataFrame(oneDayData['activities-heart-intraday']['dataset'])
            df.columns= ["Time", "HR_(BPM)"]
            name =  [subj for i in range(len(df.index))]
            date = [str(oneDate)[:10] for i in range(len(df.index))]
            df["Participant"] = name
            df["Date"] = date
            df = df[['Participant', 'Date', 'Time', 'HR_(BPM)']]
            df_list.append(df)
        except:
            print(f'No HR data for {subj} on {oneDate}')

    if len(df_list) > 0:
        #stitching together all the dataframes
        final_df = pd.concat(df_list)
        final_df.sort_values(by = ['Participant','Date','Time'])

        return final_df
    else:
        return pd.DataFrame()


def steps_summary(auth2_client, dates, subj, p, past):
    start_date = None
    date = []
    s = []
    name = []

    # finding first date not counted already
    for d in dates:
        if str(d)[:10] in past.loc[past['Participant'] == subj, 'Date'].tolist():
            print(f'Step summary for {subj} on {str(d)[:10]} already counted')
            continue
        start_date = d
        break

    # getting sleep time series and converting it into a data frame
    try:
        timeSeries = auth2_client.time_series('activities/steps', base_date=dates[0], end_date=dates[-1])
        for d in timeSeries['activities-steps']:
            date.append(d['dateTime'])
            s.append(d['value'])
            name.append(subj)
        df = pd.DataFrame({'Participant': name, 'Date': date, 'Steps': s})
    except:
        print(f'All steps for {subj} are already counted')

    try:
        return df
    except:
        return pd.DataFrame()

    ### remove duplicates

     
   

def get_steps(auth2_client, dates, subj, p, past):
    df_list = []
    for oneDate in dates:
        if str(oneDate)[:10] in past.loc[past['Participant'] == subj, 'Date'].tolist():
            print(f'Steps for {subj} on {str(oneDate)[:10]} already counted')
            continue
        try:
            oneDayData = auth2_client.intraday_time_series('activities/steps', base_date = oneDate, detail_level= '1min')
            df = pd.DataFrame(oneDayData['activities-steps-intraday']['dataset'])
            df.columns= ["Time", "Steps"]
            name =  [subj for i in range(len(df.index))]
            date = [str(oneDate)[:10] for i in range(len(df.index))]
            df["Participant"] = name
            df["Date"] = date
            df = df[['Participant', 'Date', 'Time', 'Steps']]
            df_list.append(df)
        except:
            print(f'No step data for {subj} on {oneDate}')

    if len(df_list) > 0:
        #stitching together all the dataframes
        final_df = pd.concat(df_list)
        final_df.sort_values(by = ['Participant','Date','Time'])  

        return final_df
    else:
        return pd.DataFrame()

      
# creating OAuth2 user for pushes and calls  
def set_client(row):
    #bringing in global variable into function 

    CLIENT_ID = row['client_id']
    CLIENT_SECRET= row['secret']

    print(CLIENT_ID)
    print(CLIENT_SECRET)

    # setting call and collecting access token --> make into helper function 
    server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
    server.browser_authorize()
    ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
    REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])

    return fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET,oauth2=True,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)


  
if __name__ == '__main__':
    main()