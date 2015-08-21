# Strategy
# 1, Obtain Filtered Stock list 'stock_Selected'
# 2, Obtain History ClosePrice from csv file like 'TS_Hist.csv'
# 3, Calculate Adjusted Price
# 4, Build 'macd_structure' using History/Now prices
# 5, Perform Bottom Structure Detection

# Reminder: use Pandas TimeStamp to select data:
# 1, Text Format 'xxxx/xx/xx':'xxxx/xx/xx' the latter time is included in the selection
# 2, Datetime/Date type Start_Date:End_Date the latter time is not included in the selection
# datetime objects are specific hours, minutes, and seconds even though they were not explicitly specified (they are 0)

import talib as tb
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import pandas as pd
from CAL.PyCAL import *
from lib.pyQuant import *

bandwidth = 4
recentwidth = 7
barGap = 10
analysis_Ticks = [15, 30, 60] # x.Min MACD Bottom Structure Detection

stock_Selected = pd.read_csv('RangeLow_Selected.csv', encoding='utf-8', index_col=0)
for x in analysis_Ticks:
	stock_Selected[str(x) + 'Min_Tick'] = False
	stock_Selected[str(x) + 'Min_Timing'] = ''

cal = Calendar('CHINA.SSE')
end_Date = cal.advanceDate(Date.todaysDate(), Period('-1D'), BizDayConvention.Preceding).toDateTime().date()
start_Date = cal.advanceDate(end_Date, Period('-3W'), BizDayConvention.Preceding).toDateTime().date()
stock_data = pd.read_csv('TS_Hist.csv', encoding='utf-8', parse_dates=True, index_col=0)
stock_data.index.name = 'Date'
stock_data.columns.name = 'StockNum'
stock_Selected_List = [x.split('.')[0] for x in stock_Selected.index.values]
stock_data = stock_data.ix[start_Date.isoformat():end_Date.isoformat(), stock_Selected_List]
Adj_Data = DataAPI.MktEqudGet(secID=u"",ticker=stock_data.columns.values,tradeDate=u"",beginDate=start_Date.strftime('%Y%m%d'),endDate=cal.advanceDate(Date.fromDateTime(end_Date), Period('0D'), BizDayConvention.Preceding).strftime('%Y%m%d'),field=u"secID,ticker,tradeDate,closePrice,accumAdjFactor,highestPrice",pandas="1")
Adj_Data = pd.DataFrame({'accumAdjFactor':Adj_Data['accumAdjFactor'].values, 'secID':Adj_Data['secID'].values}, index=pd.MultiIndex.from_tuples(list(zip(Adj_Data['ticker'].values, Adj_Data['tradeDate'].values)), names=['Stock', 'Date']))

for stock in stock_data.columns.values:
	for trade_day in np.unique([x.date() for x in stock_data.index.to_pydatetime()]):
		stock_data[trade_day.isoformat()][stock] *= Adj_Data.loc[stock, trade_day.isoformat()]['accumAdjFactor']

for stock in stock_data.columns.values:
	try:
		nowPrices = DataAPI.MktBarRTIntraDayGet(securityID=Adj_Data.loc[stock]['secID'][0],startTime=u"09:30",endTime=u"",pandas="1")
		nowPrices = nowPrices.rename(index=pd.to_datetime(nowPrices['barTime']))
		# Two Series with different Name: no Name for the New appended Series
		macd_structure = pd.DataFrame(stock_data[stock].append(nowPrices['closePrice']), columns={'closePrice'})
	except:
		macd_structure = pd.DataFrame(stock_data[stock].values, columns={'closePrice'}, index=stock_data.index)
	for x in analysis_Ticks:
		x_structure = macd_structure.resample(str(x)+'min', how='last',closed='right', label='right')
		x_structure = x_structure[~pd.isnull(x_structure['closePrice'])]
		closePrices = x_structure['closePrice'].values
		tradeTiming = x_structure.index.values
		macd, macdsignal, macdhist = tb.MACD(closePrices, fastperiod=12, slowperiod=26, signalperiod=9)
		isMinBuy, MinBuyTiming = isBuyingTime(macd, closePrices, tradeTiming, bandwidth, recentwidth, barGap)
		if MinBuyTiming:
			MinBuyTiming = pd.to_datetime(str(MinBuyTiming)).strftime('%Y-%m-%d  %H:%M:%S')
		stock_Selected.loc[Adj_Data.loc[stock]['secID'][0], str(x) + 'Min_Tick'] = isMinBuy
		stock_Selected.loc[Adj_Data.loc[stock]['secID'][0], str(x) + 'Min_Timing'] = MinBuyTiming
stock_Selected
