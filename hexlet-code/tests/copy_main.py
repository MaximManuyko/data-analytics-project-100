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


def ads_download():
    url = 'https://drive.google.com/uc?id=1pwrFxZKf-fNiFwv8DIzt5bNhlzcxvmcz'
    response = requests.get(url)

    # Получаем директорию, содержащую файл с кодом
    script_directory = os.path.dirname(__file__)

    # Составляем путь к файлу в той же директории
    file_path = os.path.join(script_directory, 'ads.csv')

    with open(file_path, 'wb') as file:
        file.write(response.content)

    df_ads = pd.read_csv(file_path)
    
    return df_ads

df_ads = ads_download()


API_URL = "https://data-charts-api.hexlet.app"
DATE_BEGIN = '2023-03-01'
DATE_END = '2023-09-01'


def visits_API():
    
    response = requests.get(f"{API_URL}/visits?begin={DATE_BEGIN}&end={DATE_END}")

    data = response.json()

    df_visits = pd.DataFrame(data)

    return df_visits

df_visits = visits_API()


def registrations_API():

    response = requests.get(f"{API_URL}/registrations?begin={DATE_BEGIN}&end={DATE_END}")

    data = response.json()

    df_registrations = pd.DataFrame(data)

    return df_registrations

df_registrations = registrations_API()


def visit_grouped():

    response = requests.get(f"{API_URL}/visits?begin={DATE_BEGIN}&end={DATE_END}")

    data = response.json()

    df_visits = pd.DataFrame(data)

    df_visits['datetime'] = pd.to_datetime(df_visits['datetime'])

    idx = df_visits.groupby('visit_id')['datetime'].idxmax()

    df_filtered_visits = df_visits.loc[idx]

    df_filtered_visits = df_filtered_visits[~df_filtered_visits['user_agent'].str.contains('bot', case=False)]

    df_filtered_visits['datetime'] = df_filtered_visits['datetime'].dt.strftime('%Y-%m-%d')

    df_grouped = df_filtered_visits.groupby(['datetime', 'platform']).size().reset_index(name='visits')

    df_grouped.columns = ['date_group', 'platform', 'visits']

    df_visit_grouped = df_grouped.sort_values(by='date_group')

    return df_visit_grouped

df_visit_grouped = visit_grouped()


def registrations_grouped():

    response = requests.get(f"{API_URL}/registrations?begin={DATE_BEGIN}&end={DATE_END}")

    data = response.json()

    df_registrations = pd.DataFrame(data)

    df_registrations['date_group'] = pd.to_datetime(df_registrations['datetime']).dt.strftime('%Y-%m-%d')

    df_grouped = df_registrations.groupby(['date_group', 'platform']).size().reset_index(name='registrations')

    df_registrations_grouped = df_grouped.sort_values(by=['date_group'])

    return df_registrations_grouped

df_registrations_grouped = registrations_grouped()


def conversion():

    result_df = pd.merge(df_visit_grouped, df_registrations_grouped, on=['date_group', 'platform'], how='outer')

    result_df['conversion'] = (result_df['registrations'] / result_df['visits']) * 100

    result_df['conversion'] = result_df['conversion'].round(2)

    df_conversion = result_df.sort_values(by='date_group')

    current_directory = os.path.dirname(os.path.abspath(__file__))

    json_file_path = os.path.join(current_directory, 'conversion.json')

    df_conversion.to_json(json_file_path)

    return df_conversion

df_conversion = conversion()


def ads():

    df_ads['date'] = pd.to_datetime(df_ads['date'])

    df_ads['date'] = df_ads['date'].dt.strftime('%Y-%m-%d')

    df_ads.rename(columns={'date': 'date_group'}, inplace=True)

    return df_ads

df_ads = ads()


def ads_group():

    df_ads.rename(columns={'date': 'date_group', 'utm_campaign': 'campaign'}, inplace=True)

    df_ads_group = df_ads.groupby(['date_group', 'campaign']).agg({
    'cost': 'sum'
    }).reset_index()[['date_group', 'cost', 'campaign']]

    return df_ads_group

df_ads_group = ads_group()


def out():

    df_out = pd.merge(df_ads_group, df_conversion, on='date_group', how='outer', suffixes=('_ads', '_conversion'))
    df_out['cost'].fillna(0, inplace=True)

    df_out['utm_campaign'] = df_out['campaign']
    column_order = ['date_group', 'visits', 'registrations', 'conversion', 'cost', 'utm_campaign']
    df_out = df_out[column_order]

    df_out.loc[df_out['utm_campaign'].isnull(), 'utm_campaign'] = 'none'

    df_out.sort_values(by='date_group', inplace=True)
    df_out.reset_index(drop=True, inplace=True)
    DATE_BEGIN = pd.to_datetime("2023-03-01")
    END = pd.to_datetime("2023-09-01") - pd.Timedelta(days=1)
    df_out['date_group'] = pd.to_datetime(df_out['date_group'])
    df_out = df_out[(df_out['date_group'] >= DATE_BEGIN) & (df_out['date_group'] <= DATE_END)]

    return df_out

df_out = out()


def save_ads_json():

    current_directory = os.path.dirname(os.path.abspath(__file__))

    json_file_path = os.path.join(current_directory, 'ads.json')

    df_conversion.to_json(json_file_path)

save_ads_json()


def graf_total_visits():

    df_graf_visit_grouped = df_visit_grouped.copy(deep=True)

    result_df = df_graf_visit_grouped.groupby('date_group')['visits'].sum().reset_index()
    result_df['date_group'] = pd.to_datetime(result_df['date_group'])

    plt.figure(figsize=(20, 10))
    plt.bar(result_df['date_group'], result_df['visits'], color='skyblue')

    plt.xlabel('Date Group')
    plt.ylabel('Visits')
    plt.title('Total Visits')

    mondays = WeekdayLocator(MONDAY)
    plt.gca().xaxis.set_major_locator(mondays)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    plt.xticks(rotation=45, ha='right')

    mean_value = result_df['visits'].mean()
    plt.axhline(y=mean_value, color='red', linestyle='--', label='Mean Visits')

    plt.grid(axis='y', linestyle='--', alpha=0.7)


    plt.legend()
    plt.tight_layout()

    # Получаем текущую директорию, в которой находится файл с кодом
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Формируем путь для сохранения файла в текущей директории
    file_path = os.path.join(current_directory, 'total_visits_chart.png')

    # Сохраняем график
    plt.savefig(file_path, bbox_inches='tight')

graf_total_visits()


def graf_visit_grouped_platform():

    df_graf_visit_grouped_platform = df_visit_grouped.copy(deep=True)

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

    # Получаем текущую директорию, в которой находится файл с кодом
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Формируем путь для сохранения файла в текущей директории
    file_path = os.path.join(current_directory, 'total_visits_platform_chart.png')

    # Сохраняем график
    plt.savefig(file_path, bbox_inches='tight')

graf_visit_grouped_platform()


def graf_total_registrations():

    df_graf_registrations_grouped = df_registrations_grouped.copy(deep=True)

    df_graf_registrations_grouped = df_graf_registrations_grouped.groupby('date_group')['registrations'].sum().reset_index()

    plt.figure(figsize=(20, 10))

    plt.bar(df_graf_registrations_grouped['date_group'], df_graf_registrations_grouped['registrations'], color='skyblue', alpha=0.7, label='Registrations')

    mean_value = df_graf_registrations_grouped['registrations'].mean()
    plt.axhline(y=mean_value, color='red', linestyle='--', label='Mean Value')

    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.title('Total Registrations')

    plt.xticks(df_graf_registrations_grouped['date_group'][::7], rotation=45, ha='right')

    plt.legend()

    # Получаем текущую директорию, в которой находится файл с кодом
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Формируем путь для сохранения файла в текущей директории
    file_path = os.path.join(current_directory, 'total_registrations_chart.png')

    # Сохраняем график
    plt.savefig(file_path, bbox_inches='tight')

graf_total_registrations()


def graf_total_registrations_platform():

    df_registrations_copy = df_registrations.copy(deep=True)

    df_registrations_copy['date_group'] = pd.to_datetime(df_registrations_copy['datetime'], format='%a, %d %b %Y %H:%M:%S GMT').dt.strftime('%Y-%m-%d')

    grouped_df = df_registrations_copy.groupby(['date_group', 'platform']).size().reset_index(name='registration')

    fig, ax = plt.subplots(figsize=(20, 10))

    for platform in grouped_df['platform'].unique():
        platform_data = grouped_df[grouped_df['platform'] == platform]
        ax.bar(platform_data['date_group'], platform_data['registration'], label=platform)

    ax.set_xlabel('Date Group')
    ax.set_ylabel('Registration')
    ax.set_title('Registrations by Platform')
    ax.legend()

    ax.grid(True, axis='y')

    x_labels = grouped_df['date_group'].unique()[::7]
    ax.set_xticks(x_labels)
    ax.set_xticklabels(x_labels, rotation=45, ha='right')

    # Получаем текущую директорию, в которой находится файл с кодом
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Формируем путь для сохранения файла в текущей директории
    file_path = os.path.join(current_directory, 'total_registrations_platform_chart.png')

    # Сохраняем график
    plt.savefig(file_path, bbox_inches='tight')

graf_total_registrations_platform()


def graf_registration_type_copy():

    df_graf_registration_type_copy = df_registrations.copy(deep=True)
    df_graf_registration_platform_copy = df_registrations.copy(deep=True)

    df_graf_registration_type_copy = df_graf_registration_type_copy.groupby('registration_type').size().reset_index(name='registration')
    df_graf_registration_platform_copy = df_graf_registration_platform_copy.groupby('platform').size().reset_index(name='registration')

    fig, ax = plt.subplots(1, 2, figsize=(20, 10))

    ax[0].pie(df_graf_registration_type_copy['registration'], labels=df_graf_registration_type_copy['registration_type'], autopct='%1.1f%%', startangle=90)
    ax[0].set_title('Registration by Type')

    ax[1].pie(df_graf_registration_platform_copy['registration'], labels=df_graf_registration_platform_copy['platform'], autopct='%1.1f%%', startangle=90)
    ax[1].set_title('Registration by Platform')

    # Получаем текущую директорию, в которой находится файл с кодом
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Формируем путь для сохранения файла в текущей директории
    file_path = os.path.join(current_directory, 'registration_type_platform_chart.png')

    # Сохраняем график
    plt.savefig(file_path, bbox_inches='tight')

graf_registration_type_copy()


def conversion_platform():

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

    # Получаем текущую директорию, в которой находится файл с кодом
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Формируем путь для сохранения файла в текущей директории
    file_path = os.path.join(current_directory, 'conversion_platform_chart.png')

    # Сохраняем график
    plt.savefig(file_path, bbox_inches='tight')

conversion_platform()

def conversion_total():

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

    # Получаем текущую директорию, в которой находится файл с кодом
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Формируем путь для сохранения файла в текущей директории
    file_path = os.path.join(current_directory, 'conversion_total_chart.png')

    # Сохраняем график
    plt.savefig(file_path, bbox_inches='tight')

conversion_total()


def ads_total():

    df_ads_total = df_ads.copy(deep=True)

    df_ads_total = df_ads_total.groupby('date_group')['cost'].sum().reset_index()

    df_ads_total.plot(x='date_group', y='cost', kind='line', linestyle='-', figsize=(20, 10))

    plt.title('Total cost')
    plt.xlabel('date_group')
    plt.ylabel('cost')
    plt.grid(True)

    # Получаем текущую директорию, в которой находится файл с кодом
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Формируем путь для сохранения файла в текущей директории
    file_path = os.path.join(current_directory, 'cost_total_chart.png')

    # Сохраняем график
    plt.savefig(file_path, bbox_inches='tight')

ads_total()


def visit_ads():
    
    df_ads_group_1 = df_ads.copy(deep=True)
    df_ads_group_1 = df_ads_group_1.groupby(['date_group', 'utm_source', 'utm_medium', 'campaign'], as_index=False)['cost'].sum()

    df_graf_visit_grouped_1 = df_visit_grouped.copy(deep=True)
    df_graf_visit_grouped_1 = df_graf_visit_grouped_1.groupby('date_group')['visits'].sum().reset_index()

    df_graf_registrations_grouped_1 = df_registrations_grouped.copy(deep=True)

    df_graf_registrations_grouped_1 = df_graf_registrations_grouped_1.groupby('date_group')['registrations'].sum().reset_index()

    grouped_df = df_ads_group_1.groupby(['utm_source', 'utm_medium', 'campaign'])
    result_df = pd.DataFrame(columns=['date_group_start', 'date_group_end', 'Ads'])

    for group, group_df in grouped_df:
        start_date = group_df['date_group'].min()
        end_date = group_df['date_group'].max()
        ads_name = '-'.join(group)
    
        result_df = pd.concat([result_df, pd.DataFrame({'date_group_start': [start_date],
                                                        'date_group_end': [end_date],
                                                        'Ads': [ads_name]})], ignore_index=True)
    

    grouped_df = df_ads_group_1.groupby(['utm_source', 'utm_medium', 'campaign'])
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


    # Получаем текущую директорию, в которой находится файл с кодом
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Формируем путь для сохранения файла в текущей директории
    file_path = os.path.join(current_directory, 'visits_during_marketing_active_days.png')

    # Сохраняем график
    plt.savefig(file_path, bbox_inches='tight')

visit_ads()


def registrations_ads():

    df_ads_group_1 = df_ads.copy(deep=True)
    df_ads_group_1 = df_ads_group_1.groupby(['date_group', 'utm_source', 'utm_medium', 'campaign'], as_index=False)['cost'].sum()

    df_graf_registrations_grouped_1 = df_registrations_grouped.copy(deep=True)

    df_graf_registrations_grouped_1 = df_graf_registrations_grouped_1.groupby('date_group')['registrations'].sum().reset_index()

    grouped_df = df_ads_group_1.groupby(['utm_source', 'utm_medium', 'campaign'])
    result_df = pd.DataFrame(columns=['date_group_start', 'date_group_end', 'Ads'])

    for group, group_df in grouped_df:
        start_date = group_df['date_group'].min()
        end_date = group_df['date_group'].max()
        ads_name = '-'.join(group)
    
        result_df = pd.concat([result_df, pd.DataFrame({'date_group_start': [start_date],
                                                        'date_group_end': [end_date],
                                                        'Ads': [ads_name]})], ignore_index=True)
    

    grouped_df = df_ads_group_1.groupby(['utm_source', 'utm_medium', 'campaign'])
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
    plt.title('Registrations during marketing active days')
    plt.xlabel('date_group')
    plt.ylabel('registrations')
    plt.xticks(df_graf_registrations_grouped_1['date_group'][::7], rotation=45, ha='right')

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())


    # Получаем текущую директорию, в которой находится файл с кодом
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Формируем путь для сохранения файла в текущей директории
    file_path = os.path.join(current_directory, 'registrations_during_marketing_active_days.png')

    # Сохраняем график
    plt.savefig(file_path, bbox_inches='tight')

registrations_ads()

print('Ok')