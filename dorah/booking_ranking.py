import gower
import numpy as np
import pandas as pd
import sqlite3
import re

conn = sqlite3.connect('booking_database.db')
cursor = conn.cursor()
cursor.execute("SELECT name, location, price, distance, rating, number_of_rooms, amenities FROM booking_data")
data = cursor.fetchall()
#print(data)


conn.close()

#numpy_array = np.array(data)

#numpy_array[:, 3] = np.array([re.sub(r'[^\d.]', '', str(x)) for x in numpy_array[:, 3]]).astype(float)


#numpy_array[:, 2] = numpy_array[:, 2].astype(float)
#numpy_array[:, 3] = numpy_array[:, 3].astype(float)
#numpy_array[:, 4] = numpy_array[:, 4].astype(float)
#numpy_array[:, 5] = numpy_array[:, 5].astype(float)

#print(numpy_array)

# Convert to DataFrame
df = pd.DataFrame(data, columns=["name", "location", "price", "distance", "rating", "number_of_rooms", "amenities"])

# Clean numeric fields
df['distance'] = df['distance'].apply(lambda x: float(re.sub(r'[^\d.]', '', str(x))))
df['price'] = df['price'].astype(float)
df['rating'] = df['rating'].astype(float)
df['number_of_rooms'] = df['number_of_rooms'].astype(float)

# insert og property in pandas data
og_property = {
    'name': ['Elektra Property'],
    'location': ['1400 Hubbell Pl, Seattle, WA 98101, USA'],
    'price': [200],
    'distance': [0],
    'rating': [8],
    'number_of_rooms': [2]
    }
new_row = pd.DataFrame(og_property)
df = pd.concat([new_row, df]).reset_index(drop=True)

# Run Gower distance
gower.gower_matrix(df, cat_features=[True, True, False, False, False, False])

gower_topn_index = gower.gower_topn(df.iloc[0:1,:], df.iloc[:,], n=11)['index']

pd.set_option('display.max_columns', None) 
pd.set_option('display.width', 1000)             # Set max line width for wrapping (adjust as needed)
#pd.set_option('display.max_colwidth', None)  
print(df.iloc[gower_topn_index])
