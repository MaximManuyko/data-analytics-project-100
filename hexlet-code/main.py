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


def save_graf(name_png):
    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    #charts_directory = os.path.join(current_directory, 'charts')
    charts_directory = os.path.join(current_directory)
    if not os.path.exists(charts_directory):
        os.makedirs(charts_directory)
    plt.savefig(os.path.join(charts_directory, f'{name_png}.png'), bbox_inches='tight')


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
    

def graf(df_conversion_group_no_platform, df_visits_API, df_registrations_API):

#graf_total_visits

    df_conversion_group_no_platform = ads_json()
    df_conversion_group_no_platform_copy = df_conversion_group_no_platform.copy()

    plt.figure(figsize=(20, 10))
    plt.bar(df_conversion_group_no_platform_copy['date_group'], df_conversion_group_no_platform_copy['visits'], color='blue')
    mean_value = df_conversion_group_no_platform_copy['visits'].mean()
    plt.axhline(y=mean_value, color='red', linestyle='--', label='Mean Visits')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xlabel('Date Group')
    plt.ylabel('Visits')
    plt.title('Total Visits')
    plt.xticks(rotation=45)
    
    save_graf('total_visits_chart')


#graf_visit_grouped_platform

    df_visits_group = conversion(df_visits_API, df_registrations_API)
    df_graf_visit_grouped_platform = df_visits_group.copy(deep=True)
    df_graf_visit_grouped_platform['date_group'] = pd.to_datetime(df_graf_visit_grouped_platform['date_group'])
    fig, ax = plt.subplots(figsize=(20, 10))
    df_graf_visit_grouped_platform.groupby(['date_group', 'platform']).sum()['visits'].unstack().plot(kind='bar', stacked=True, ax=ax)
    ax.set_xlabel('date_group')
    ax.set_ylabel('visits')
    ax.set_title('Visits by platform')
    ax.legend(title='platform')
    ax.yaxis.grid(True)
    plt.xticks(rotation=45, ha='right')
    ax.xaxis.set_major_locator(plt.MaxNLocator(30))
    save_graf('total_visits_platform_chart')


#graf_total_registrations
    
    df_conversion_group_no_platform = ads_json()
    df_conversion_group_no_platform_copy = df_conversion_group_no_platform.copy()
    plt.figure(figsize=(20, 10))
    plt.bar(df_conversion_group_no_platform_copy['date_group'], df_conversion_group_no_platform_copy['registrations'], color='red')
    mean_value = df_conversion_group_no_platform_copy['registrations'].mean()
    plt.axhline(y=mean_value, color='blue', linestyle='--', label='Mean registrations')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xlabel('Date Group')
    plt.ylabel('registrations')
    plt.title('Total registrations')
    plt.xticks(rotation=45)
    
    save_graf('total_registrations_chart')


#graf_registrations_grouped_platform
    df_visits_group = conversion(df_visits_API, df_registrations_API) 
    df_graf_visit_grouped_platform = df_visits_group.copy(deep=True)
    df_graf_visit_grouped_platform['date_group'] = pd.to_datetime(df_graf_visit_grouped_platform['date_group'])
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ['red', 'yellow', 'green']  # Задайте цвета в нужном порядке
    df_graf_visit_grouped_platform.groupby(['date_group', 'platform']).sum()['registrations'].unstack().plot(kind='bar', stacked=True, ax=ax, color=colors)
    ax.set_xlabel('date_group')
    ax.set_ylabel('registrations')
    ax.set_title('registrations by platform')
    ax.legend(title='platform')
    ax.yaxis.grid(True)
    plt.xticks(rotation=45, ha='right')
    ax.xaxis.set_major_locator(plt.MaxNLocator(30))

    save_graf('total_registrations_platform_chart')


#conversion_platform
    df_conversion = conversion(df_visits_API, df_registrations_API)
    df_conversion_copy = df_conversion.copy(deep=True)

    android_data = df_conversion_copy[df_conversion_copy['platform'] == 'android']
    ios_data = df_conversion_copy[df_conversion_copy['platform'] == 'ios']
    web_data = df_conversion_copy[df_conversion_copy['platform'] == 'web']

    fig, axs = plt.subplots(3, 1, figsize=(20, 15), sharex=False, sharey=False)
    axs[0].plot(android_data['date_group'], android_data['conversion'], label='Android')
    axs[0].set_title('Conversion для Android')
    axs[0].set_ylabel('Conversion (%)')
    axs[0].legend()
    axs[0].grid(True, linestyle='-', linewidth=2, alpha=0.5, which='both', axis='y', markevery=2)
    axs[0].tick_params(axis='x', rotation=45)  # Поворот меток оси x
    axs[0].xaxis.set_major_locator(plt.MaxNLocator(nbins=30))

    axs[1].plot(ios_data['date_group'], ios_data['conversion'], label='iOS')
    axs[1].set_title('Conversion для iOS')
    axs[1].set_ylabel('Conversion (%)')
    axs[1].legend()
    axs[1].grid(True, linestyle='-', linewidth=2, alpha=0.5, which='both', axis='y', markevery=2)
    axs[1].tick_params(axis='x', rotation=45) 
    axs[1].xaxis.set_major_locator(plt.MaxNLocator(nbins=30)) 

    axs[2].plot(web_data['date_group'], web_data['conversion'], label='Web')
    axs[2].set_title('Conversion для Web')
    axs[2].set_xlabel('date_group')
    axs[2].set_ylabel('Conversion (%)')
    axs[2].legend()
    axs[2].grid(True, linestyle='-', linewidth=2, alpha=0.5, which='both', axis='y', markevery=2)
    axs[2].tick_params(axis='x', rotation=45) 
    axs[2].xaxis.set_major_locator(plt.MaxNLocator(nbins=30))

    plt.tight_layout()

    save_graf('conversion_platform_chart')
    

#conversion_total
    df_conversion = conversion(df_visits_API, df_registrations_API)
    df_conversion_total = df_conversion.copy(deep=True)

    grouped_df = df_conversion_total.groupby('date_group').agg({'visits': 'sum', 'registrations': 'sum'})
    grouped_df['conversion'] = (grouped_df['registrations'] / grouped_df['visits'] * 100).round(2)

    plt.figure(figsize=(20, 10))
    plt.plot(grouped_df.index, grouped_df['conversion'], linestyle='-')
    plt.title('Conversion Total')
    plt.xlabel('date_group')
    plt.ylabel('Conversion (%)')
    plt.grid(which='major', axis='y', linestyle='-', linewidth=1.5, color='gray', alpha=0.7)
    plt.gca().xaxis.set_major_locator(MultipleLocator(10))
    plt.xticks(rotation=45, ha='right')

    save_graf('conversion_total_chart')
    

#ads_total
    ads_group = ads_download()
    df_ads_total = ads_group.copy(deep=True)
    df_ads_total = df_ads_total.groupby('date_group')['cost'].sum().reset_index()
    df_ads_total.plot(x='date_group', y='cost', kind='line', linestyle='-', figsize=(20, 10))

    plt.title('Total cost')
    plt.xlabel('date_group')
    plt.ylabel('cost')
    plt.grid(True)

    save_graf('ads_total_chart')


#visit_ads
    df_ads = ads_download()

    df_ads_group_1 = df_ads.copy(deep=True)
    df_ads_group_1 = df_ads_group_1.groupby(['date_group', 'utm_source', 'utm_medium', 'utm_campaign'], as_index=False)['cost'].sum()

    df_conversion_group_no_platform = ads_json()

    df_graf_visit_grouped_1 = df_conversion_group_no_platform.copy(deep=True)
    df_graf_visit_grouped_1 = df_graf_visit_grouped_1.groupby('date_group')['visits'].sum().reset_index()

    df_graf_registrations_grouped_1 = df_conversion_group_no_platform.copy(deep=True)

    df_graf_registrations_grouped_1 = df_graf_registrations_grouped_1.groupby('date_group')['registrations'].sum().reset_index()

    grouped_df = df_ads_group_1.groupby(['utm_source', 'utm_medium', 'utm_campaign'])
    result_df = pd.DataFrame(columns=['date_group_start', 'date_group_end', 'Ads'])

    for group, group_df in grouped_df:
        start_date = group_df['date_group'].min()
        end_date = group_df['date_group'].max()
        ads_name = '-'.join(group)
    
        result_df = pd.concat([result_df, pd.DataFrame({'date_group_start': [start_date],
                                                        'date_group_end': [end_date],
                                                        'Ads': [ads_name]})], ignore_index=True)
    

    grouped_df = df_ads_group_1.groupby(['utm_source', 'utm_medium', 'utm_campaign'])
    result_df = pd.DataFrame(columns=['date_group_start', 'date_group_end', 'Ads'])

    for group, group_df in grouped_df:
        start_date = group_df['date_group'].min()
        end_date = group_df['date_group'].max()
        ads_name = '-'.join(group)
    
        result_df = pd.concat([result_df, pd.DataFrame({'date_group_start': [start_date],
                                                        'date_group_end': [end_date],
                                                        'Ads': [ads_name]})], ignore_index=True)

    num_colors = len(result_df['Ads'].unique())
    ads_colors = plt.cm.rainbow(np.linspace(0, 1, num_colors))

    ads_color_dict = dict(zip(result_df['Ads'].unique(), ads_colors))

    plt.figure(figsize=(20, 10))
    plt.plot(df_graf_visit_grouped_1['date_group'], df_graf_visit_grouped_1['visits'], label='visits')

    for index, row in result_df.iterrows():
        plt.axvspan(row['date_group_start'], row['date_group_end'], facecolor=ads_color_dict[row['Ads']], alpha=0.5, label=row['Ads'])

    plt.grid(which='major', axis='y', linestyle='-', linewidth=1.5, color='gray', alpha=0.7)
    plt.title('Visits during marketing active days')
    plt.xlabel('date_group')
    plt.ylabel('visits')
    plt.xticks(df_graf_visit_grouped_1['date_group'][::7], rotation=45, ha='right')

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    save_graf('visit_ads_chart')


#registrations_ads
    df_ads = ads_download()

    df_ads_group_1 = df_ads.copy(deep=True)
    df_ads_group_1 = df_ads_group_1.groupby(['date_group', 'utm_source', 'utm_medium', 'utm_campaign'], as_index=False)['cost'].sum()

    df_conversion_group_no_platform = ads_json()

    df_graf_visit_grouped_1 = df_conversion_group_no_platform.copy(deep=True)
    df_graf_visit_grouped_1 = df_graf_visit_grouped_1.groupby('date_group')['visits'].sum().reset_index()

    df_graf_registrations_grouped_1 = df_conversion_group_no_platform.copy(deep=True)

    df_graf_registrations_grouped_1 = df_graf_registrations_grouped_1.groupby('date_group')['registrations'].sum().reset_index()

    grouped_df = df_ads_group_1.groupby(['utm_source', 'utm_medium', 'utm_campaign'])
    result_df = pd.DataFrame(columns=['date_group_start', 'date_group_end', 'Ads'])

    for group, group_df in grouped_df:
        start_date = group_df['date_group'].min()
        end_date = group_df['date_group'].max()
        ads_name = '-'.join(group)
    
        result_df = pd.concat([result_df, pd.DataFrame({'date_group_start': [start_date],
                                                        'date_group_end': [end_date],
                                                        'Ads': [ads_name]})], ignore_index=True)
    

    grouped_df = df_ads_group_1.groupby(['utm_source', 'utm_medium', 'utm_campaign'])
    result_df = pd.DataFrame(columns=['date_group_start', 'date_group_end', 'Ads'])

    for group, group_df in grouped_df:
        start_date = group_df['date_group'].min()
        end_date = group_df['date_group'].max()
        ads_name = '-'.join(group)
    
        result_df = pd.concat([result_df, pd.DataFrame({'date_group_start': [start_date],
                                                        'date_group_end': [end_date],
                                                        'Ads': [ads_name]})], ignore_index=True)

    num_colors = len(result_df['Ads'].unique())
    ads_colors = plt.cm.rainbow(np.linspace(0, 1, num_colors))

    ads_color_dict = dict(zip(result_df['Ads'].unique(), ads_colors))

    plt.figure(figsize=(20, 10))
    plt.plot(df_graf_registrations_grouped_1['date_group'], df_graf_registrations_grouped_1['registrations'], label='registrations')

    for index, row in result_df.iterrows():
        plt.axvspan(row['date_group_start'], row['date_group_end'], facecolor=ads_color_dict[row['Ads']], alpha=0.5, label=row['Ads'])

    plt.grid(which='major', axis='y', linestyle='-', linewidth=1.5, color='gray', alpha=0.7)
    plt.title('registrations during marketing active days')
    plt.xlabel('date_group')
    plt.ylabel('registrations')
    plt.xticks(df_graf_registrations_grouped_1['date_group'][::7], rotation=45, ha='right')

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    save_graf('registrations_ads_chart')




def run_all():
    df_visits_API = visits_API_download()
    df_registrations_API = registrations_API_download()
    conversion(df_visits_API, df_registrations_API)
    ads_download()
    ads_json()
    df_conversion_group_no_platform = ads_json()
    graf(df_conversion_group_no_platform, df_visits_API, df_registrations_API)


if __name__ == "__main__":
    run_all()