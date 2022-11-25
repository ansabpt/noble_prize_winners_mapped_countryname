import requests
import pandas as pd



def get_noble_prize_winners():
    endpoint = "http://api.nobelprize.org/v1/laureate.json"
    res = requests.get(endpoint).json()
    return res
def get_countries():
    endpoint = "http://api.nobelprize.org/v1/country.json"
    res = requests.get(endpoint).json()
    return res

try:
    #get API Response
    response = get_noble_prize_winners()
    if response:
        laureates=response['laureates']
        df = pd.DataFrame.from_dict(laureates)
        #Select Required Columns from the api response
        df=df[['id','firstname','surname','born','prizes','gender','bornCountryCode']]
        #expand prize to get year and category
        df1= df.explode('prizes').reset_index(drop=True)
        df1 = pd.DataFrame.from_records(df1['prizes'].values)
        df=df.join(df1).drop(columns = ['prizes'])
        #merge two column values to give name
        df['name'] = df['firstname'] + ' ' +df['surname']
        #fill values with space if null
        df['surname'] = df['surname'].fillna(' ')
        df['bornCountryCode'] = df['bornCountryCode'].astype(str)
        #get lookup table to map country names with country code
        country_res = get_countries()
        dict = country_res['countries']
        df_country = pd.DataFrame.from_dict(dict)
        df_country=df_country[['name','code']]
        #renaming columns to left join with the first dataframe
        df_country.columns=['country_name','bornCountryCode']
        df_country = df_country.drop_duplicates(subset=['bornCountryCode'])
        df_country['bornCountryCode'] = df_country['bornCountryCode'].astype(str)
        df_final = pd.merge(df,df_country,on='bornCountryCode',how='left')
        #selecting specified columns from the file to give a clean output file
        df_final = df_final[['id','name','born','gender','bornCountryCode','country_name','year','category']]
        df_final.columns =['id','name','born','gender','bornCountryCode','country_name','unique_prize_years','unique_prize_categories']
        df_final.to_csv("final.csv",index=False)
except Exception as e:
    print(e)
