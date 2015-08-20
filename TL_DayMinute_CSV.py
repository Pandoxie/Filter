# -*- coding: utf-8 -*-
import numpy as np
import datetime as dt
import pandas as pd

stock_all = DataAPI.MktEqudLatelyGet(field=u"",pandas="1")
stock_data = pd.DataFrame({})
bars = pd.DataFrame({})
stock_data_list = []
count = 0
totalNum = len(stock_all)
for stock in stock_all['secID'].values:
	try:
		bars = DataAPI.MktBarRTIntraDayGet(securityID=stock,startTime=u"",endTime=u"",pandas="1")
	except:
		count += 1
		continue
	if bars['closePrice'].min() == bars['closePrice'].max(): bars['closePrice'] = np.nan
	stock_data_list.append(bars.rename(index=pd.to_datetime(bars['barTime']), columns={'closePrice' : stock})[stock])
	count += 1
	print str(float(count)/totalNum*100) + '%'
stock_data = pd.concat(stock_data_list, axis=1)
stock_data.to_csv('stock_data_' + dt.date.today().isoformat() + '.csv', encoding='utf-8')

#pd.read_csv('stock_data_' + dt.date.today().isoformat() + '.csv', encoding='utf-8', parse_dates=True, index_col=0)