from pprint import pprint
import pandas as pd
import numpy as np
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

path = "auto.csv"

auto_df = pd.read_csv(path, header=None)

#adding header to data
headers= ["symboling","normalized-losses","make","fuel-type","aspiration", "num-of-doors","body-style",
         "drive-wheels","engine-location","wheel-base", "length","width","height","curb-weight","engine-type",
         "num-of-cylinders", "engine-size","fuel-system","bore","stroke","compression-ratio","horsepower",
         "peak-rpm","city-mpg","highway-mpg","price"]
auto_df.columns=headers

#replacing null values
auto_df.replace('?',np.NaN, inplace=True)

# dropping rows with null value in price
auto_df.dropna(subset=['price'],axis=0, inplace=True)

#to find missing data
missing_data=auto_df.isnull()

#for column in missing_data:
#   print(column)
#   print(missing_data[column].value_counts())
#   print("")

# in normalised loss counting mean
avg_norm_loss=auto_df['normalized-losses'].astype(float).mean()

#replacing missing data with mean value for normalised losses
auto_df['normalized-losses'].replace(np.nan,avg_norm_loss,inplace=True)

#in bore calculating mean
avg_bore=auto_df['bore'].astype(float).mean()

#replacing missing data with mean value for bore
auto_df['bore'].replace(np.nan,avg_bore,inplace=True)

#in stroke counting mean
avg_stroke= auto_df['stroke'].astype(float).mean()

#replacing missing data with mean value for stroke
auto_df['stroke'].replace(np.nan,avg_stroke,inplace=True)

#changing type
auto_df['bore'].astype(float)
auto_df['stroke'].astype(float)

#in horsepower calculating mean
avg_horse= auto_df['horsepower'].astype(float).mean()


#replacing missing data with mean value for horespower
auto_df['horsepower'].replace(np.nan,avg_horse,inplace=True)

#in peak rpm calculating mean
avg_rpm=auto_df['peak-rpm'].astype(float).mean()

#replacing missing data with mean value for peak-rpm
auto_df['peak-rpm'].replace(np.nan,avg_rpm,inplace=True)

#Calculatig frequency in num-of-doors
freq=auto_df['num-of-doors'].value_counts().idxmax()

#replacing missing data with frequency
auto_df['num-of-doors'].fillna(freq, inplace=True)

auto_df[['bore','stroke','peak-rpm','price']]= auto_df[['bore','stroke','peak-rpm','price']].astype(float)
auto_df[['normalized-losses','horsepower']]= auto_df[['normalized-losses','horsepower']].astype(int)

auto_df['city-L/100km']=235/auto_df['city-mpg']

auto_df['length']=auto_df['length']/auto_df['length'].max()
auto_df['width']=auto_df['width']/auto_df['width'].max()

auto_df['height']=auto_df['height']/auto_df['height'].max()

horsebin=np.linspace(auto_df['horsepower'].min(),auto_df['horsepower'].max(),4)


horsegroup=['low','medium','high']
auto_df['horsepower-binned']=pd.cut(auto_df['horsepower'],horsebin,labels=horsegroup,include_lowest=True)
auto_df['horsepower-binned']

fuel_temp=pd.get_dummies(auto_df['fuel-type'])
fuel_temp.rename(columns={'gas':'fuel-type-gas','diesel':'fuel-type-diesel'},inplace=True)

auto_df=pd.concat([auto_df,fuel_temp],axis=1)

aspiration_temp=pd.get_dummies(auto_df['aspiration'])
aspiration_temp.rename(columns={'std':'aspiration-std','turbo':'aspiration-turbo'},inplace=True)
auto_df=pd.concat([auto_df,aspiration_temp],axis=1)

auto_df.drop('fuel-type', axis=1,inplace=True)
auto_df.drop('aspiration',axis=1,inplace=True)

auto_df['horsepower-binned']=auto_df['horsepower-binned'].astype(object)

auto_df[['fuel-type-diesel','fuel-type-gas','aspiration-std','aspiration-turbo']]=auto_df[['fuel-type-diesel','fuel-type-gas','aspiration-std','aspiration-turbo']].astype(int)

wheel_drive_temp =pd.get_dummies(auto_df['drive-wheels'])

wheel_drive_temp.rename(columns={'4wd':'wheel-drive-4wd','fwd':'wheel-drive-fwd','rwd':'wheel-drive-rwd'},inplace=True)

auto_df=pd.concat([wheel_drive_temp,auto_df],axis=1)


missing_data = auto_df.isnull()
#for column in missing_data:
#   print(column)
#   print(missing_data[column].value_counts())
#   print("")



client = MongoClient("mongodb+srv://admin:5PuGTPvIEbUS12mw@automotivedb.0ihalkz.mongodb.net/test")


#creating new database
db = client['auto_db']

#creating new collection
auto_collection = db['auto_collection']

auto_records = auto_df.to_dict('records')
auto_collection.insert_many(auto_records)
