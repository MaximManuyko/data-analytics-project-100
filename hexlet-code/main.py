import pandas as pd
import requests
import matplotlib.pyplot as plt
from matplotlib.dates import WeekdayLocator, MONDAY
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
import numpy as np
from io import StringIO
from matplotlib.ticker import MultipleLocator
import os
from dotenv import load_dotenv

API_URL = "https://data-charts-api.hexlet.app"
DATE_BEGIN = '2023-03-01'
DATE_END = '2023-06-01'


def visits_API_download():
    response = requests.get(f"{API_URL}/visits?begin={DATE_BEGIN}&end={DATE_END}")
    data = response.json()
    df_visits = pd.DataFrame(data)
    df_visits.reset_index(drop=True, inplace=True)
    
    return df_visits




def registrations_API_download():
    response = requests.get(f"{API_URL}/registrations?begin={DATE_BEGIN}&end={DATE_END}")
    data = response.json()
    df_registrations = pd.DataFrame(data)
    df_registrations.reset_index(drop=True, inplace=True)
    
    return df_registrations


def conversion(df_visits_API, df_registrations_API):
    df_visits_API_not_bot = df_visits_API[df_visits_API.apply(lambda row: 'bot' not in row['user_agent'].lower(), axis=1)].copy()
    df_visits_API_not_bot['datetime'] = pd.to_datetime(df_visits_API_not_bot['datetime'])
    df_visits_API_not_bot.sort_values(by='datetime', ascending=False, inplace=True)
    df_unique_visits = df_visits_API_not_bot.groupby('visit_id').first().reset_index()
    df_unique_visits['datetime'] = pd.to_datetime(df_unique_visits['datetime'])
    df_unique_visits['date_group'] = df_unique_visits['datetime'].dt.strftime('%Y-%m-%d')
    df_visits_group = df_unique_visits.groupby(['date_group', 'platform']).size().reset_index(name='visits')

    df_registrations_group = df_registrations_API.copy()
    df_registrations_group['date_group'] = pd.to_datetime(df_registrations_API['datetime']).dt.strftime('%Y-%m-%d')
    df_registrations_group = df_registrations_group.groupby(['date_group', 'platform']).size().reset_index(name='registrations')

    df_conversion = pd.merge(df_visits_group, df_registrations_group, on=['date_group', 'platform'], how='outer')
    df_conversion = df_conversion.fillna(0)
    df_conversion['conversion'] = ((df_conversion['registrations'] / df_conversion['visits']) * 100).round(2)
    df_conversion = df_conversion.sort_values(by='date_group')

    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    df_conversion.to_json(os.path.join(current_directory, 'conversion.json'), orient='records', lines=True)
    df_conversion.reset_index(drop=True, inplace=True)

    return df_conversion


def ads_download():
    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    file_path = os.path.join(current_directory, 'ads.csv')
    df_ads = pd.read_csv(file_path)

    df_ads['date'] = pd.to_datetime(df_ads['date']).dt.strftime('%Y-%m-%d')
    df_ads_filtered = df_ads[(df_ads['date'] >= DATE_BEGIN) & (df_ads['date'] <= DATE_END)]
    ads_group = df_ads_filtered.groupby(['date', 'utm_source', 'utm_medium', 'utm_campaign'], as_index=False)['cost'].sum()
    ads_group.rename(columns={'date': 'date_group'}, inplace=True)

    return ads_group


def ads_json():
    df_visits_API = visits_API_download()
    df_registrations_API = registrations_API_download()
    df_conversion = conversion(df_visits_API, df_registrations_API)
    df_conversion_group_no_platform = df_conversion.copy()
    df_conversion_group_no_platform = df_conversion_group_no_platform.groupby('date_group').agg({
    'visits': 'sum',
    'registrations': 'sum'
}).reset_index()

    df_ads_group = ads_download()
    df_ads_json = pd.merge(df_conversion_group_no_platform, df_ads_group, on='date_group', how='outer')
    df_ads_json['cost'] = df_ads_json['cost'].fillna(0)
    df_ads_json['utm_campaign'] = df_ads_json['utm_campaign'].fillna('none')
    df_ads_json = df_ads_json[['date_group', 'visits', 'registrations', 'cost', 'utm_campaign']]
    
    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    df_ads_json.to_json(os.path.join(current_directory, 'ads.json'), orient='records', lines=True)
    
    df_ads_json.reset_index(drop=True, inplace=True)

    return df_ads_json
    
def graf(df_conversion_group_no_platform):
    df_conversion_group_no_platform_copy = df_conversion_group_no_platform.copy()
    

    
    


def run_all():
    df_visits_API = visits_API_download()
    print("df_visits_API")

    df_registrations_API = registrations_API_download()
    print("df_registrations_API")

    df_conversion = conversion(df_visits_API, df_registrations_API)
    print("df_conversion")
    print("conversion.json")

    df_ads_group = ads_download()
    print("df_ads_group")

    df_ads_json = ads_json()
    print("df_ads_json")

    df_conversion_group_no_platform = graf(df_ads_json)
    print(df_conversion_group_no_platform)

run_all()


'''    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    excel_filename = os.path.join(current_directory, 'df_ads_json.xlsx')
    df_ads_json.to_excel(excel_filename, index=False)
    print(f"DataFrame сохранен в Excel файл: {excel_filename}")'''