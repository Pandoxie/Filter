# -*- coding: utf-8 -*-
import talib as tb
import numpy as np
import datetime as dt
import pandas as pd
import tushare as ts

start_date = dt.date(2015,8,1)
end_date = dt.date.today()

stock_data = pd.read_csv('stock_data_' + start_date.isoformat() + '_' + end_date.isoformat() + '.csv', encoding='utf-8', parse_dates=True, index_col=0)
stock_data.index.name = 'Date'
stock_data.columns.name = 'StockNum'
print stock_data
