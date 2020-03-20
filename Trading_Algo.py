import numpy as np
import pandas as pd
import datetime as dt
import pandas_datareader.data as web

# Desired time frame for positional data
start = dt.datetime(2015, 2, 3)
end = dt.datetime.today()

# Create a pandas df to serve as a cleaner version of the API output
output = pd.DataFrame()

# Create a list with desired tickers to be tested
tickers = ['ITOT','AGG']

#Clean up API outputs by using our own "output" df
for ticker in tickers:
    df = web.DataReader(ticker, 'yahoo', start, end)
    output['Close ' + ticker] = df['Close']
# end

# Handling for dates, converting shitty API provided dates to string and throwing them in a column
dates =[]
for x in range(len(df)):
    newdate = str(df.index[x])
    newdate = newdate[0:10]
    dates.append(newdate)

df['dates'] = dates
output['dates'] = dates
df.append(dates)
output.append(dates)

#output.to_csv(r'C:\Users\Einst\Trading Algo Omega Pi\Outputs\Output.csv',index=None)

# Initialize the short and long windows
short_window = 40
long_window = 100

#Initiate Excel object to add data too
excel = pd.ExcelWriter('Signal_Output.xlsx')
#Start loop to perform test for multiple tickers
for ticker in tickers:
    # Initialize the `signals` DataFrame with the `signal` column
    #creating the df inside loop to reset it when looping
    signals = pd.DataFrame(index=output.index)
    #fill values as floats
    signals['signal ' + ticker] = 0.0

    # Create short simple moving average over the short window
    signals['short_mavg ' + ticker] = output['Close ' + ticker].rolling(window=short_window, min_periods=1, center=False).mean()

    # Create long simple moving average over the long window
    signals['long_mavg ' + ticker] = output['Close ' + ticker].rolling(window=long_window, min_periods=1, center=False).mean()
    
    # Create signals
    signals['signal ' + ticker] = np.where(signals['short_mavg ' + ticker]
                                                          > signals['long_mavg ' + ticker], 1.0, 0.0)   

    # Generate trading orders
    signals['positions ' + ticker] = signals['signal ' + ticker].diff()
    #Append dates
    signals.append(dates)
    #Add dataframe to excel sheet
    signals.to_excel(excel,sheet_name = ticker, index = None)
    
#end loop
#Save Excel object
excel.save()
#Append date column to final outputs
output.append(dates)

# Print `signals`
print(signals)

