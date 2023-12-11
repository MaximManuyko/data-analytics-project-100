#!/usr/bin/env python
# coding: utf-8

# Проект модуля #3
# # Дашборд конверсий
# Аналитик данных

# # Шаг 1
# ## Подготовка к работе с данными

# ### Загрузите данные по рекламам из csv

# In[38]:


get_ipython().run_cell_magic('time', '', 'import pandas as pd\nimport requests\nimport matplotlib.pyplot as plt\nfrom matplotlib.dates import WeekdayLocator, MONDAY\nimport matplotlib.dates as mdates\nfrom pandas.plotting import register_matplotlib_converters\nimport numpy as np\nfrom io import StringIO\nfrom matplotlib.ticker import MultipleLocator\n')


# In[39]:


get_ipython().run_cell_magic('time', '', "\nresponse = requests.get('https://drive.google.com/uc?id=1pwrFxZKf-fNiFwv8DIzt5bNhlzcxvmcz')\ncsv_data = StringIO(response.text)\n\ndf_ads = pd.read_csv(csv_data)\n\ndf_ads.head()\n")


# ### Изучите данные, сделайте предварительный анализ с помощью dataframe.describe

# In[40]:


df_ads.describe(include='all')


# ### Визиты из CSV

# In[41]:


df_visits_csv = pd.read_csv("https://drive.google.com/uc?id=1QosQQ4RRNR9rkL4t7sB707h2Uy0XfYJe")

df_visits_csv.head()


# In[42]:


df_visits_csv.describe(include='all')


# ### Регистрации из CSV

# In[43]:


df_registrations_csv = pd.read_csv("https://drive.google.com/uc?id=1AeQz0kaSgz0lxYSDtuNm36muhy5fRCzZ")

df_registrations_csv.head()


# In[44]:


df_registrations_csv.describe(include='all')


# # Шаг 2
# ## Запросы к API
# ### Запросите данные по API за период 2023-03-01 -> 2023-09-01

# ### Визиты

# In[45]:


START = "2023-03-01"
END = "2023-09-01"


# In[46]:


get_ipython().run_cell_magic('time', '', '\nresponse = requests.get(f"https://data-charts-api.hexlet.app/visits?begin={START}&end={END}")\n\ndata = response.json()\n\ndf_visits = pd.DataFrame(data)\n\ndf_visits.head()\n')


# In[47]:


df_visits.describe(include='all')


# ### Регистрации

# In[48]:


get_ipython().run_cell_magic('time', '', '\nresponse = requests.get(f"https://data-charts-api.hexlet.app/registrations?begin={START}&end={END}")\n\ndata = response.json()\n\ndf_registrations = pd.DataFrame(data)\n\ndf_registrations.head()\n')


# In[49]:


get_ipython().run_cell_magic('time', '', "\ndf_registrations.describe(include='all')\n")


# # Шаг 3
# 
# ## Расчет метрик
# 
# ### Сгруппируйте данные визитов по датам и платформам

# In[50]:


get_ipython().run_cell_magic('time', '', '\nresponse = requests.get(f"https://data-charts-api.hexlet.app/visits?begin={START}&end={END}")\ndata = response.json()\n\ndf_visits = pd.DataFrame(data)\n\ndf_visits[\'datetime\'] = pd.to_datetime(df_visits[\'datetime\'])\n\nidx = df_visits.groupby(\'visit_id\')[\'datetime\'].idxmax()\n\ndf_filtered_visits = df_visits.loc[idx]\n\ndf_filtered_visits = df_filtered_visits[~df_filtered_visits[\'user_agent\'].str.contains(\'bot\', case=False)]\n\ndf_filtered_visits[\'datetime\'] = df_filtered_visits[\'datetime\'].dt.strftime(\'%Y-%m-%d\')\n\ndf_grouped = df_filtered_visits.groupby([\'datetime\', \'platform\']).size().reset_index(name=\'visits\')\n\ndf_grouped.columns = [\'date_group\', \'platform\', \'visits\']\n\ndf_visit_grouped = df_grouped.sort_values(by=\'date_group\')\n\ndf_visit_grouped.head()\n')


# In[51]:


df_visit_grouped.describe(include='all')


# ### Сгруппируйте также данные регистраций по датам и платформам

# In[52]:


get_ipython().run_cell_magic('time', '', 'response = requests.get(f"https://data-charts-api.hexlet.app/registrations?begin={START}&end={END}")\ndata = response.json()\n\ndf_registrations = pd.DataFrame(data)\n\ndf_registrations[\'date_group\'] = pd.to_datetime(df_registrations[\'datetime\']).dt.strftime(\'%Y-%m-%d\')\n\ndf_grouped = df_registrations.groupby([\'date_group\', \'platform\']).size().reset_index(name=\'registrations\')\n\ndf_registrations_grouped = df_grouped.sort_values(by=[\'date_group\'])\n\ndf_registrations_grouped.head()\n')


# In[53]:


df_registrations_grouped.describe(include='all')


# ### Объедините датайфреймы, сделайте итоговый датафрейм с расчетом конверсии
# 
# ### Сохраните датафрейм в формате JSON conversion.json

# In[54]:


get_ipython().run_cell_magic('time', '', "result_df = pd.merge(df_visit_grouped, df_registrations_grouped, on=['date_group', 'platform'], how='outer')\n\nresult_df['conversion'] = (result_df['registrations'] / result_df['visits']) * 100\n\nresult_df['conversion'] = result_df['conversion'].round(2)\n\ndf_conversion = result_df.sort_values(by='date_group')\n\ndf_conversion.to_json('conversion.json')\n\ndf_conversion.head()\n")


# In[55]:


df_conversion.describe(include='all')


# # Шаг 4
# 
# ## Добавляем рекламы
# 
# ### В этом шаге добавим данные по рекламным кампаниям

# In[56]:


get_ipython().run_cell_magic('time', '', '\ndf_ads = pd.read_csv("https://drive.google.com/uc?id=1pwrFxZKf-fNiFwv8DIzt5bNhlzcxvmcz")\n\ndf_ads[\'date\'] = pd.to_datetime(df_ads[\'date\'])\n\ndf_ads[\'date\'] = df_ads[\'date\'].dt.strftime(\'%Y-%m-%d\')\n\ndf_ads.rename(columns={\'date\': \'date_group\'}, inplace=True)\n\ndf_ads.head()\n')


# In[57]:


df_ads.describe(include='all')


# In[58]:


get_ipython().run_cell_magic('time', '', "\ndf_ads.rename(columns={'date': 'date_group', 'utm_campaign': 'campaign'}, inplace=True)\n\ndf_ads_group = df_ads.groupby(['date_group', 'campaign']).agg({\n    'cost': 'sum'\n}).reset_index()[['date_group', 'cost', 'campaign']]\n\ndf_ads_group.head()\n")


# In[59]:


df_ads_group.describe(include='all')


# In[60]:


df_out = pd.merge(df_ads_group, df_conversion, on='date_group', how='outer', suffixes=('_ads', '_conversion'))

df_out['cost'].fillna(0, inplace=True)
df_out['campaign'].fillna('none', inplace=True)

column_order = ['date_group', 'platform', 'visits', 'registrations', 'conversion', 'cost', 'campaign']
df_out = df_out[column_order]

df_out.sort_values(by='date_group', inplace=True)

df_out.reset_index(drop=True, inplace=True)

START = pd.to_datetime("2023-03-01")
END = pd.to_datetime("2023-09-01") - pd.Timedelta(days=1)

df_out['date_group'] = pd.to_datetime(df_out['date_group'])

df_out = df_out[(df_out['date_group'] >= START) & (df_out['date_group'] <= END)]

df_out.head()


# In[61]:


df_out.describe(include='all')


# In[62]:


#df_out.to_json("out.json", orient='records', lines=True)
df_out.to_json("out.json")


# # Шаг 5
# 
# ## Визуализация
# 
# ### Итоговые визиты

# In[63]:


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

plt.savefig('charts/total_visits_chart.png', bbox_inches='tight')

plt.show()


# ### Итоговые визиты с разбивкой по платформам: web, android, ios, bot

# In[64]:


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

plt.savefig('charts/total_visits_platform_chart.png', bbox_inches='tight')

plt.show()


# ### Итоговые регистрации

# In[65]:


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

plt.savefig('charts/total_registrations_chart.png')

plt.show()


# ### Итоговые регистрации с разбивкой по платформе: web, android, ios

# In[66]:


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

plt.savefig('charts/total_registrations_platform_chart.png')

plt.show()


# ### Итоговые регистрации с разбивкой по типу регистрации: email, google, apple, yandex

# In[67]:


df_graf_registration_type_copy = df_registrations.copy(deep=True)
df_graf_registration_platform_copy = df_registrations.copy(deep=True)

df_graf_registration_type_copy = df_graf_registration_type_copy.groupby('registration_type').size().reset_index(name='registration')
df_graf_registration_platform_copy = df_graf_registration_platform_copy.groupby('platform').size().reset_index(name='registration')

fig, ax = plt.subplots(1, 2, figsize=(20, 10))

ax[0].pie(df_graf_registration_type_copy['registration'], labels=df_graf_registration_type_copy['registration_type'], autopct='%1.1f%%', startangle=90)
ax[0].set_title('Registration by Type')

ax[1].pie(df_graf_registration_platform_copy['registration'], labels=df_graf_registration_platform_copy['platform'], autopct='%1.1f%%', startangle=90)
ax[1].set_title('Registration by Platform')

plt.savefig('charts/registration_type_platform_chart.png')

plt.show()


# ### Конверсия по каждой платформе

# In[68]:


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

plt.savefig('charts/conversion_platform_chart.png')

plt.show()


# ### Средняя конверсия <span style="color:red;">(Общая)</span>
# 

# In[69]:


df_conversion_total = df_conversion.copy(deep=True)

grouped_df = df_conversion_total.groupby('date_group').agg({'visits': 'sum', 'registrations': 'sum'})

grouped_df['conversion'] = (grouped_df['registrations'] / grouped_df['visits'] * 100).round(2)

plt.figure(figsize=(20, 10))
plt.plot(grouped_df.index, grouped_df['conversion'], linestyle='-')

plt.title('Conversion Total')
plt.xlabel('date_group')
plt.ylabel('Conversion (%)')

plt.xticks(df_graf_registrations_grouped['date_group'][::7], rotation=45, ha='right')

plt.grid(which='major', axis='y', linestyle='-', linewidth=1.5, color='gray', alpha=0.7)

plt.gca().xaxis.set_major_locator(MultipleLocator(10))

plt.savefig('charts/conversion_total_chart.png')

plt.show()


# ### Стоимости реклам

# In[70]:


df_ads_total = df_ads.copy(deep=True)

df_ads_total = df_ads_total.groupby('date_group')['cost'].sum().reset_index()

df_ads_total.plot(x='date_group', y='cost', kind='line', linestyle='-', figsize=(20, 10))

plt.title('Total cost')
plt.xlabel('date_group')
plt.ylabel('cost')
plt.grid(True)

plt.savefig('charts/cost_total_chart.png')

plt.show()


# ### Визиты за весь период с цветовым выделением рекламной кампании

# In[71]:


df_ads_group_1 = df_ads.copy(deep=True)
df_ads_group_1 = df_ads_group_1.groupby(['date_group', 'utm_source', 'utm_medium', 'campaign'], as_index=False)['cost'].sum()

df_graf_visit_grouped_1 = df_visit_grouped.copy(deep=True)
df_graf_visit_grouped_1 = df_graf_visit_grouped_1.groupby('date_group')['visits'].sum().reset_index()

df_graf_registrations_grouped_1 = df_registrations_grouped.copy(deep=True)

df_graf_registrations_grouped_1 = df_graf_registrations_grouped_1.groupby('date_group')['registrations'].sum().reset_index()


# In[74]:


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

plt.savefig('charts/visits_during_marketing_active_days.png')

plt.show()


# ### Регистрации за весь период с цветовым выделением рекламной кампании

# In[75]:


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

plt.savefig('charts/registrations_during_marketing_active_days.png')

plt.show()


# In[ ]:




