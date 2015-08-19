# -*- coding: utf-8 -*-
import talib as tb
import numpy as np
import datetime as dt
import pandas as pd
import tushare as ts

start_date = dt.date(2015,8,1)
end_date = dt.date.today()
stock_basic = ts.get_stock_basics()

stock_data = pd.DataFrame({})
stock_data_list = []
count = 0
totalNum = len(stock_basic)
for stock in stock_basic.index.values:
	stock_data_list.append(ts.get_hist_data(stock, start=start_date.isoformat(), end=end_date.isoformat(), ktype='15', retry_count = 10).rename(columns={'close' : stock})[stock])
	count += 1
	print str(float(count)/totalNum*100) + '%'
stock_data = pd.concat(stock_data_list, axis=1)

stock_data.to_csv('stock_data_' + start_date.isoformat() + '_' + start_date.isoformat() + '.csv', encoding='utf-8')
