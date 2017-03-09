import pandas as pd

df = pd.read_csv('fx_events.csv')
df.sort_values( by = ['date', 'time', 'currency'], inplace = True )
cols_order = ['date','weekday','time','currency','impact','event','eventid','actual','forecast','previous']
df[cols_order].to_csv('fx_events.csv', index = False)
