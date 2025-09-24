# BOOKING_RANKING.PY
# -----
# ranks properties in database using gower matrix
# ranks based on address, distance, rating, number of rooms, amenities
# prints ten most similar properties to inputted property
# -----

# import libraries
import gower
import numpy as np
import pandas as pd
import sqlite3
import re

# REPLACE BELOW INFORMATION WITH INFO ABT SPECIFIC PROPERTY
input_property = {
    'name': ['Elektra Property'],
    'location': ['1400 Hubbell Pl, Seattle, WA 98101, USA'],
    'price': [200],
    'distance': [0],
    'rating': [8],
    'number_of_rooms': [2],
    'amenities': ["good breakfast, wifi, free parking"]
    }

# creates sqlite database connection
conn = sqlite3.connect('booking_database.db')
cursor = conn.cursor()

# retrieves data from sqlite database
cursor.execute("SELECT name, location, price, distance, rating, number_of_rooms, amenities FROM booking_data")
data = cursor.fetchall()

# close connection
conn.close()

# convert to pandas dataframe
df = pd.DataFrame(data, columns=["name", "location", "price", "distance", "rating", "number_of_rooms", "amenities"])

# clean numberic data
df['distance'] = df['distance'].apply(lambda x: float(re.sub(r'[^\d.]', '', str(x))))
df['price'] = df['price'].astype(float)
df['rating'] = df['rating'].astype(float)
df['number_of_rooms'] = df['number_of_rooms'].astype(float)

# insert original property into top row of dataframe
new_row = pd.DataFrame(input_property)
df = pd.concat([new_row, df]).reset_index(drop=True)

# drop all columns not relevant to final search (name, price, address)
name_column = df['name']
df = df.drop(columns=['name'])

price_column = df['price']
df = df.drop(columns=['price'])

address_column = df['location']
df = df.drop(columns=['location'])

# run gower calculations
gower.gower_matrix(df, cat_features=[False, False, False, True])
gower_topn_index = gower.gower_topn(df.iloc[0:1,:], df.iloc[:,], n=11)['index']

# reinsert dropped columns back into dataframe
df.insert(0, 'name', name_column)
df.insert(1, 'price', price_column)
df.insert(2, 'address', address_column)

# format final output to display all columns and print
pd.set_option('display.max_columns', None)
print(df.iloc[gower_topn_index])
