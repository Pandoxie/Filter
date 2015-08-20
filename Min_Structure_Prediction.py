import talib as tb
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
from pandas import *
from CAL.PyCAL import *

def isBuyingTime(macd, closePrices, tradeTiming, bandwidth):
	macd_diff = np.diff(np.array(macd))
	count = bandwidth - 1
	buying_Ticks = []
	while count < len(macd_diff):
		if count != len(macd_diff)-1 and np.all(macd_diff[count-bandwidth+1:count+1] <= 0) and macd_diff[count+1] > 0:
			buying_Ticks.append(count+1)
		count += 1
	if len(buying_Ticks) >= 2 and (len(macd) - 1 - buying_Ticks[-1]) <= recentwidth and (max(buying_Ticks) - min(buying_Ticks) > 10):
		prev_Tick = [x for x in buying_Ticks if buying_Ticks[-1]-x >= barGap][-1]
		if (min(closePrices[buying_Ticks[-1]-1:buying_Ticks[-1]+2]) < min(closePrices[prev_Tick-1:prev_Tick+2])) and (macd[buying_Ticks[-1]] > macd[prev_Tick]):
			return (True, tradeTiming[buying_Ticks[-1]])
	return (False, '')

bandwidth = 4
recentwidth = 7
barGap = 10

stock_Selected = pd.read_csv('RangeLow_Selected.csv', encoding='utf-8', index_col=0)
stock_Selected['15_MinuteBuy_Tick'] = False
stock_Selected['15_MinuteBuy_Timing'] = ''

cal = Calendar('CHINA.SSE')
end_Date = cal.advanceDate(Date.todaysDate(), Period('0D'), BizDayConvention.Preceding).toDateTime()
start_Date = cal.advanceDate(end_Date, Period('-3W'), BizDayConvention.Preceding).toDateTime()
stock_data = pd.read_csv('Hist_Min.csv', encoding='utf-8', parse_dates=True, index_col=0)
stock_data.index.name = 'Date'
stock_data.columns.name = 'StockNum'
stock_Selected_List = [x.split('.')[0] for x in stock_Selected.index.values]
stock_data = stock_data.ix[start_Date:end_Date, stock_Selected_List]
Adj_Data = DataAPI.MktEqudGet(secID=u"",ticker=stock_data.columns.values,tradeDate=u"",beginDate=start_Date.strftime('%Y%m%d'),endDate=cal.advanceDate(Date.fromDateTime(end_Date), Period('-1D'), BizDayConvention.Preceding).strftime('%Y%m%d'),field=u"secID,ticker,tradeDate,closePrice,accumAdjFactor,highestPrice",pandas="1")
Adj_Data = pd.DataFrame({'accumAdjFactor':Adj_Data['accumAdjFactor'].values, 'secID':Adj_Data['secID'].values}, index=pd.MultiIndex.from_tuples(list(zip(Adj_Data['ticker'].values, Adj_Data['tradeDate'].values)), names=['Stock', 'Date']))

for stock in stock_data.columns.values:
	for trade_day in np.unique([x.date() for x in stock_data.index.to_pydatetime()]):
		stock_data[trade_day.isoformat()][stock] *= Adj_Data.loc[stock, trade_day.isoformat()]['accumAdjFactor']

for stock in stock_data.columns.values:
	nowPrices = DataAPI.MktBarRTIntraDayGet(securityID=Adj_Data.loc[stock]['secID'][0],startTime=u"09:30",endTime=u"",pandas="1").iloc[0:-1:15]
	closePrices = np.append(stock_data.loc[~isnull(stock_data[stock]), stock].values, nowPrices['closePrice'].values)
	tradeTiming = np.append(stock_data.loc[~isnull(stock_data[stock]), stock].index.values, pd.to_datetime(nowPrices['barTime']).values)
	macd, macdsignal, macdhist = tb.MACD(closePrices, fastperiod=12, slowperiod=26, signalperiod=9)
	isMinBuy, MinBuyTiming = isBuyingTime(macd, closePrices, tradeTiming, bandwidth)
	if MinBuyTiming:
		MinBuyTiming = pd.to_datetime(str(MinBuyTiming)).strftime('%Y-%m-%d  %H:%M:%S')
	stock_Selected.loc[Adj_Data.loc[stock]['secID'][0], '15_MinuteBuy_Tick'] = isMinBuy
	stock_Selected.loc[Adj_Data.loc[stock]['secID'][0], '15_MinuteBuy_Timing'] = MinBuyTiming
stock_Selected


