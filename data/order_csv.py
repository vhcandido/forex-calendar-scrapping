import pandas as pd

# Load and sort the values
df = pd.read_csv('all_fx_events.csv')
df.sort_values( by = ['date', 'time', 'currency'], inplace = True )

# Get column names
# slower -> header = list(df)
header = df.columns.values.tolist()

# Choose columns to appear first
cols_order = ['date','weekday','time','currency','impact','event','eventid','actual','forecast','previous']
for col in header:
    if col not in cols_order:
        cols_order.append(col)

# Write data in a CSV file
df[cols_order].to_csv('fx_events.csv', index = False)
