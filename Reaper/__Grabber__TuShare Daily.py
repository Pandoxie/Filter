# -*- coding: utf-8 -*-
# Obtain Stock Market List from CSV
# Use 'isAppend' to determin whether the prog run is append mode or not


import talib as tb
import numpy as np
import datetime as dt
import pandas as pd
import tushare as ts

isAppend = True
start_date = dt.date(2015,8,1)
end_date = dt.date(2015,8,20)

stock_basic = pd.read_csv('StockList.csv', encoding='utf-8', dtype=object, index_col=0, names=['ID'], header=0)
stock_data = pd.DataFrame({})
stock_data_list = []
count = 0
totalNum = len(stock_basic)

if not isAppend:
	for stock in stock_basic['ID']:
		stock_data_list.append(ts.get_hist_data(stock, start=start_date.isoformat(), end=end_date.isoformat(), ktype='15', retry_count = 10).rename(columns={'close' : stock})[stock])
		count += 1
		print str(float(count)/totalNum*100) + '%'
	stock_data = pd.concat(stock_data_list, axis=1)
	stock_data.to_csv('TS_Hist.csv', encoding='utf-8')
else:
	old_stock_data = pd.read_csv('TS_Hist.csv', encoding='utf-8', parse_dates=True, index_col=0)
	for stock in stock_basic['ID']:
		stock_data_list.append(ts.get_hist_data(stock, start=dt.date.today().isoformat(), end=(dt.date.today()+dt.timedelta(days=1)).isoformat(), ktype='15', retry_count = 10).rename(columns={'close' : stock})[stock])
		count += 1
		print str(float(count)/totalNum*100) + '%'
	stock_data = old_stock_data.append(pd.concat(stock_data_list, axis=1))
	stock_data.to_csv('TS_Hist.csv', encoding='utf-8')

