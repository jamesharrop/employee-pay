'''
Calculate total pay for employer, using Pandas

Input is an Excel spreadsheet with columns:
Name
Pensionable: 'Yes' or 'No' (defaults to 'Yes')
Role1Hours
Role1Rate
Role1Type
Role2Hours
Role2Rate
Role2Type

Output is:
A dataframe showing total pay and the calculations
A series showing total hours per job role
'''

import numpy as np
import pandas as pd

# filename1, filename2 are defined externally
sheetname = '1'

def calculate_summary(filename, sheetname):
    df = pd.read_excel(filename, sheet_name=sheetname)

    df['Pensionable'] = df['Pensionable'].fillna('Yes') # Default to being in pension scheme
    df['Pensionable'] = df['Pensionable'].apply(lambda x: {'Yes': True, 'None': True, 'No': False}.get(x))

    df = df.fillna(0) # Then fill in zero for any NaN in other columns

    df['Role1PayPerWeek'] = df['Role1Hours'] * df['Role1Rate']
    df['Role2PayPerWeek'] = df['Role2Hours'] * df['Role2Rate']
    df['TotalPayPerWeek'] = df['Role1PayPerWeek'] + df['Role2PayPerWeek']
    df['TotalPayPerYear'] = df['TotalPayPerWeek'] * 52

    def calculate_NI(weekly_pay):
        NI_threshold = 162
        if weekly_pay > NI_threshold:
            return (weekly_pay - NI_threshold) * 13.8/100
        else:
            return 0

    df['WeeklyNI'] = df['TotalPayPerWeek'].apply(calculate_NI)

    df['AnnualPension'] = df['TotalPayPerYear'] * 14.38/100 * df['Pensionable']

    df['TotalAnnualCost'] = df['TotalPayPerYear'] + df['WeeklyNI'] * 52 + df['AnnualPension']

    annual_cost = df['TotalAnnualCost'].sum()

    role1totalhours = df.groupby('Role1Type').sum()['Role1Hours']
    role2totalhours = df.groupby('Role2Type').sum()['Role2Hours']
    role2totalhours = role2totalhours.drop(labels=[0]) # People who have no role 2

    totalhours = role1totalhours.combine(role1totalhours, lambda x,y: x+y, fill_value=0)

    totalannualcost = pd.Series([annual_cost], index=['Total annual cost'])
    summary_output = totalhours.append(totalannualcost.round(2))
    return summary_output, df

# Scenario 1
a, df1 = calculate_summary(filename1, sheetname)
df1.to_excel("output.xlsx", sheet_name=(sheetname + '_output'))

# Scenario 2
b, df2 = calculate_summary(filename2, sheetname)