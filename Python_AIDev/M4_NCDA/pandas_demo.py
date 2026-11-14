import pandas as pd

# df = pd.read_csv('chaichain_orders.csv')
# print(df.head())  
# print(df.tail())  
# print(df.info())
# print(df.describe())

#***********************************
# Creating a DataFrame
#***********************************

data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'Los Angeles', 'Chicago']
}

df = pd.DataFrame(data)
print(df)
print(df.shape)
print(df.columns)
print(df.info())

#***********************************
# Accessing DataFrame Columns
#***********************************

print(df['Name'])
print(df[['Name', 'Age']])

#***********************************
# Accessing DataFrame Rows
#***********************************

print(df.iloc[0])
print(df.iloc[0:2])
print(df.loc[df['Age'] > 30])

#***********************************
# Accessing DataFrame Elements
#***********************************

print(df.at[0, 'Name'])
print(df.iat[0, 1])

#***********************************
# Modifying DataFrame Elements
#***********************************

df.at[0, 'Name'] = 'Alex'
df.iat[0, 1] = 26
print(df)

#***********************************
# Adding and Dropping DataFrame Columns
#***********************************

df['Country'] = ['USA', 'USA', 'USA']
print(df)
df = df.drop('Country', axis=1)
print(df)

#***********************************
# Adding and Dropping DataFrame Rows
#***********************************

df = pd.concat([df, pd.DataFrame([{'Name': 'David', 'Age': 40, 'City': 'San Francisco'}])], ignore_index=True)
print(df)
df = df.drop(3, axis=0)
print(df)