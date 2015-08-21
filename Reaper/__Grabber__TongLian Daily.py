# -*- coding: utf-8 -*-

# This program is surposed to be run on a daily basis after market closure
# Basic MultiIndex Structure of Stored Data:
# Stock									000001.XSHE
# Details	closePrice	openPrice	highPrice	lowPrice	totalVolume	totalValue
# 2015-08-21 09:30:00


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
	if bars['closePrice'].min() == bars['closePrice'].max():
		count += 1
		continue
	bars = bars.rename(index=pd.to_datetime(bars['barTime']))
	bars_index = pd.MultiIndex.from_tuples(list(zip([stock]*6, ['closePrice', 'openPrice', 'highPrice', 'lowPrice', 'totalVolume', 'totalValue'])), names=['Stock', 'Details'])
	bars = pd.DataFrame(np.transpose([bars['closePrice'].values, bars['openPrice'].values, bars['highPrice'].values, bars['lowPrice'].values, bars['totalVolume'].values, bars['totalValue'].values]), columns=bars_index, index=bars.index.values)
	stock_data_list.append(bars)
	count += 1
	print str(float(count)/totalNum*100) + '%'
stock_data = pd.concat(stock_data_list, axis=1)
stock_data.to_csv('stock_data_' + dt.date.today().isoformat() + '.csv', encoding='utf-8')

# pd.read_csv('stock_data_' + dt.date.today().isoformat() + '.csv', encoding='utf-8', parse_dates=True, index_col=0, header=[0,1])