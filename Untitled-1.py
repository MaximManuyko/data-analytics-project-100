import os
import pandas as pd
import requests

def ads_download():
    url = 'https://drive.google.com/uc?id=1pwrFxZKf-fNiFwv8DIzt5bNhlzcxvmcz'
    response = requests.get(url)

    script_directory = os.path.dirname(__file__)

    file_path = os.path.join(script_directory, 'ads.csv')

    with open(file_path, 'wb') as file:
        file.write(response.content)

    df_ads = pd.read_csv(file_path)
    
    return df_ads

df_ads = ads_download()

print(df_ads)
