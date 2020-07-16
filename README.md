# trade 

## tracker
The tracker module calculates the gain and total fees from a series of trades exported from Coinbase in CSV format

version 0.1.0 - calculates gain and total fees only - 
assumes one portfolio, one product, one size unit, and one price unit -
short-term and long-term gains not differentiated

### Options

`--filename` the name of the CSV file placed in the same folder as tracker.py
(default: trades.csv)
    
`--debug`
    if true, run in debug mode
    (default: False)

