import pandas as pd
import csv, json
import requests
from requests import Session
from nsetools import Nse
import datetime as dt
from datetime import time
import os
import time as t
import argparse

#Arguments
parser = argparse.ArgumentParser(description="This is NSE option chain script")
parser.add_argument("-index_code", '--index_name', action="store", dest='index_name', help="Index Name Required", type=str)
parser.add_argument("-expiry", '--expiry_date', action="store", dest='expiry_date', help="expiry dd-mmm-ccyy", type=str)
args = parser.parse_args()

#This will return current price of stock / index. Currently implmented for index
def get_current(stock, symbol_type):
    nse = Nse()
    if symbol_type == 'index':
        last_traded_price = json.loads(json.dumps(nse.get_index_quote(stock)))
    else:
        last_traded_price = json.loads(json.dumps(nse.get_quote(stock)))
    return last_traded_price

# This function will get stricker, expiry and return the option chain for CE and PE calls
def connect_and_get_options(expiry, current_price):
    url_oc = 'https://www.nseindia.com/option-chain'
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
        "accept-language": "en-US,en;q=0.9,hi;q=0.8", "accept-encoding": "gzip, deflate, br"}

    session = requests.Session()
    request = session.get(url_oc, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    response = session.get(url, headers=headers, timeout=5, cookies=cookies).json()

    #print(response)

    call_data = [data['CE'] for data in response['records']['data'] if "CE" in data and data['expiryDate'] == expiry]
    put_data = [data['PE'] for data in response['records']['data'] if "PE" in data and data['expiryDate'] == expiry]

    call_data= pd.DataFrame(call_data).sort_values(['strikePrice'])
    put_data = pd.DataFrame(put_data).sort_values(['strikePrice'])

    call_strike_infcous = (call_data.loc[call_data['strikePrice']> current_price].head(5)).append(
        call_data.loc[call_data['strikePrice'] < current_price].head(5))
    put_strike_infocus = (put_data.loc[call_data['strikePrice']> current_price].head(5)).append(
        put_data.loc[call_data['strikePrice'] < current_price].head(5))

    call_strike_sorted = pd.DataFrame(call_strike_infcous).sort_values(['strikePrice'])
    call_strike_sorted = call_strike_sorted[['strikePrice','openInterest','changeinOpenInterest','totalTradedVolume',
    'expiryDate','lastPrice']]

    put_strike_sorted =  pd.DataFrame(put_strike_infocus).sort_values(['strikePrice'])
    put_strike_sorted =  put_strike_sorted[['strikePrice','openInterest','changeinOpenInterest','totalTradedVolume',
    'expiryDate','lastPrice']]
    return call_strike_sorted, put_strike_sorted

def get_hours_minutes():
    return dt.datetime.today().strftime('%Y-%m-%d-%H:%m')

def append_timestamp(call_option_stikes, put_option_Strikes,current_price) :
    extract_timestamp = get_hours_minutes()

    call_option_stikes['timestamp']= extract_timestamp
    put_option_Strikes['timestamp'] = extract_timestamp

    call_option_stikes['currentPrice'] = current_price
    put_option_Strikes['currentPrice'] = current_price

    return call_option_stikes, put_option_Strikes

def wriet_tofile(option_chain, filename):
    if not os.path.exists(filename):
        option_chain.to_csv(filename, mode='w', header= True)
    else:
        option_chain.to_csv(filename,mode='a', header=False)

def extract_option_chain (stock_code,file_path,expiry):
    current_stock_price= get_current(stock_code,'index')
    ce_option_chain, pe_option_chain = connect_and_get_options(expiry,current_stock_price)
    ce_option_chain, pe_option_chain = append_timestamp(ce_option_chain,pe_option_chain,current_stock_price)
    option_chain = pd.DataFrame.merge(ce_option_chain,pe_option_chain, on=['strikePrice','currentPrice', 'timestamp'], how='inner',
                                      suffixes=('_CE', '_PE'))
    wriet_tofile(option_chain, file_path)

def extract_info(stock_code, file_path, expiry):
    start_time_of_day = dt.datetime.combine(dt.date.today(), time(9,30,42))
    next_run_time = start_time_of_day
    end_time_of_day = dt.datetime.combine(dt.date.today(),time(15,30,42))

    interval = 15
    sleep_secs = 60*5 #sleep for 5 minutes

    file_suffix = dt.date.today().strftime("%Y%m%d")
    file_suffix = file_suffix + '.csv'
    file_path += file_suffix

    while True:
        if dt.datetime.now() >= start_time_of_day:
            extract_option_chain(stock_code,file_path,expiry)
            next_run_time = start_time_of_day +dt.timedelta(minutes=interval)
            break
    while True:
        if dt.datetime.now() >= end_time_of_day:
            break
        elif dt.datetime.now() >= next_run_time:
            extract_option_chain(stock_code,file_path,expiry)
            next_run_time = start_time_of_day +dt.timedelta(minutes=interval)
            t.sleep(sleep_secs)

def main ():
        extract_info(args.index_name, 'D:\\OptionChainData\\nifty_options_',args.expiry_date)

if __name__ == '__main__':
    main()
