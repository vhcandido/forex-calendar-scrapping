#!/usr/bin/env python

import pandas as pd
import sys

def main(filename):
    # Load and sort the values
    df = pd.read_csv(filename)
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
    df[cols_order].to_csv(filename, index = False)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Expected argument.\nExiting...'
        exit(1)
    else:
        main(sys.argv[1])
