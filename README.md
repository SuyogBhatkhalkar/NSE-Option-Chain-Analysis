# NSE-Option-Chain-Analysis
This module is analyze National Stock Exchange (India) Option chain data . 
The project has two modules: 
  1. Data Colection: Python script to fork NSE option data availabel at https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY  after every 15 mins and store it as csv file on the local desktop.
  2. Jupyter notebook py file to plot various grap on the collected data like change In Open Interest wrt time, Change in Price wrt time for selected strikes, Change in underlying index price, Change in Volume. 
 
 Above plots will help traders to determine beloww long , short underwriting  and unwinding happening in option chain thruout the day as well as Dyanmic support and resistance level for the day. This infomration will help traders to make decision and make positions in options. 
 Few concepts:
 Long Unwinding: Close out Position of Long, i.e Selling the stocks to exit the long position.
 Short Covering: Close out Position of Short, i.e Buying back the stocks to exit the short position.
 
