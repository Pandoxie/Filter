# Basics of Stock Price Process
# 1, Get price
# 2, Multiply Price with accumAdjFactor
# 3, Filter Suspension Prices

# First part of program gets 'stock_Selected' by criteria (1, not suspended; 2, ChangeRate more than 'stockChangeLimit') and performs Bottom Structure Detection
# Second part of program performs Win/Lose Prediction than computes 'Expectation' of this strategy
# 1, Buy Stock after 'Future_Gap' days after valid BS at opening price
# 2, Perform daily Win/Lose Exit(1,-1) or Hold Limit Exit(0) check
# 3, Calculate Expectation

import talib as tb
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import pandas as pd
from CAL.PyCAL import *
from lib.pyQuant import *

bandwidth = 4	# Num of consecutive pos/neg bars that may indicate a turnaround
recentwidth = 7	# Within how many bars a structure would to be considered valid, otherwise it may be obsolete
stockChangeLimit = -0.4 # Num that filters stock's change rate
barGap = 10 # Turnarounds minimum distance
start_date = Date(2015, 6, 15)
end_date = Date(2015, 8, 11)
top_List = 50

# Strategy Setup
Future_Gap = 2 # Num of days to actually buy a stock after Structure Detection
up_Limit = 0.2 # Win Exit Threshold
down_Limit = -up_Limit/2 # Lose Exit THreshold
hold_Limit = 20 # Max days to hold stock

cal = Calendar('CHINA.SSE')
start_date = cal.advanceDate(start_date, Period('0D'), BizDayConvention.Preceding)
end_date = cal.advanceDate(end_date, Period('0D'), BizDayConvention.Preceding)
macd_start_date = cal.bizDatesList(start_date - Period('60D'), end_date)[-33 - len(cal.bizDatesList(start_date, end_date))]

MarketSnapShot = DataAPI.MktTickRTSnapshotGet(securityID=u"",field=u"ticker,exchangeCD,lastPrice,shortNM,dataDate,dataTime,suspension",pandas="1")
StockSnapShot = DataAPI.MktEqudGet(secID=u"",ticker=u"",tradeDate=end_date.strftime('%Y%m%d'),beginDate=u"",endDate=u"",field=u"",pandas="1")
StockSnapShot['closePrice'] = StockSnapShot['closePrice'] * StockSnapShot['accumAdjFactor']
StockSnapShot['Price_Change'] = np.nan
StockSnapShot['DayBuy_Tick'] = False
StockSnapShot['MinuteBuy_Tick'] = False
StockSnapShot['Suspension'] = False
StockSnapShot['avg_Gain'] = np.nan
StockSnapShot['Buy_Signal_Date'] = ''
StockSnapShot['Exit_Status'] = np.nan
StockSnapShot['Exit_Date'] = ''
StockSnapShot['Hold_Days'] = np.nan

for stock in StockSnapShot['secID']:
	StockSnapShot.ix[StockSnapShot['secID']==stock, 'Suspension'] = StockSnapShot.ix[StockSnapShot['secID']==stock, 'highestPrice'].values[0] == 0
	stockHistPrice = DataAPI.MktEqudGet(secID=stock,ticker=u"",tradeDate=u"",beginDate=macd_start_date.strftime('%Y%m%d'),endDate=end_date.strftime('%Y%m%d'),field=u"tradeDate,highestPrice,closePrice,accumAdjFactor",pandas="1")
	stockHistPrice['closePrice'] = stockHistPrice['closePrice'] * stockHistPrice['accumAdjFactor']
	stockHistPrice = stockHistPrice[stockHistPrice['highestPrice'] != 0]
	stockHistHigh = stockHistPrice.ix[[Date.parseISO(x) >= start_date for x in stockHistPrice['tradeDate'].values], 'closePrice'].max()
	stockNowPrice = StockSnapShot[StockSnapShot['secID']==stock]['closePrice'].values[0]
	stockChange = (stockNowPrice - stockHistHigh)/stockHistHigh
	StockSnapShot.ix[StockSnapShot['secID']==stock, 'Price_Change'] = stockChange
	if stockChange <= stockChangeLimit/2:
		closePrices = stockHistPrice['closePrice'].values
		tradeDates = stockHistPrice['tradeDate'].values
		macd, macdsignal, macdhist = tb.MACD(closePrices, fastperiod=12, slowperiod=26, signalperiod=9)
		StockSnapShot.ix[StockSnapShot['secID']==stock, 'DayBuy_Tick'], StockSnapShot.ix[StockSnapShot['secID']==stock, 'Buy_Signal_Date'] = isBuyingTime(macd, closePrices, tradeDates, bandwidth, recentwidth, barGap)

stock_Selected = StockSnapShot[StockSnapShot['Suspension']==False].sort(columns='Price_Change', ascending=True).head(top_List).loc[:, ['secID', 'secShortName', 'closePrice', 'Price_Change', 'DayBuy_Tick', 'Buy_Signal_Date', 'Exit_Status', 'Exit_Date', 'Hold_Days', 'avg_Gain']]

if end_date < Date.todaysDate() and len(cal.bizDatesList(end_date, cal.advanceDate(Date.todaysDate(), Period('0D'), BizDayConvention.Preceding))) > hold_Limit:
	for stock in stock_Selected[stock_Selected['DayBuy_Tick']]['secID']:
		stockBuyPrice = DataAPI.MktEqudGet(secID=stock,ticker=u"",tradeDate=(cal.advanceDate(Date.parseISO(stock_Selected.ix[stock_Selected['secID']==stock, 'Buy_Signal_Date'].values[0]), Period(str(Future_Gap)+'D'), BizDayConvention.Following)).strftime('%Y%m%d'),beginDate=u"",endDate=u"",field=u"tradeDate,openPrice,accumAdjFactor",pandas="1")
		stockBuyPrice['openPrice'] = stockBuyPrice['openPrice'] * stockBuyPrice['accumAdjFactor']
		stockBuyPrice = stockBuyPrice['openPrice'].values[0]
		hold_DayCount = Future_Gap + 1
		stockFuturePrice = DataAPI.MktEqudGet(secID=stock,ticker=u"",tradeDate=(cal.advanceDate(Date.parseISO(stock_Selected.ix[stock_Selected['secID']==stock, 'Buy_Signal_Date'].values[0]), Period(str(hold_DayCount)+'D'), BizDayConvention.Following)).strftime('%Y%m%d'),beginDate=u"",endDate=u"",field=u"tradeDate,highestPrice,lowestPrice,accumAdjFactor",pandas="1")
		while True:
			stockFuturePrice['highestPrice'] = stockFuturePrice['highestPrice'] * stockFuturePrice['accumAdjFactor']
			stockFuturePrice['lowestPrice'] = stockFuturePrice['lowestPrice'] * stockFuturePrice['accumAdjFactor']
			if stockFuturePrice['highestPrice'].values[0] != 0 and (stockFuturePrice['highestPrice'].values[0] - stockBuyPrice)/stockBuyPrice >= up_Limit:
				stock_Selected.ix[stock_Selected['secID']==stock, 'Exit_Status'] = 1
				stock_Selected.ix[stock_Selected['secID']==stock, 'Hold_Days'] = hold_DayCount - Future_Gap
				stock_Selected.ix[stock_Selected['secID']==stock, 'Exit_Date'] = stockFuturePrice['tradeDate'].values[0]
				break
			elif stockFuturePrice['lowestPrice'].values[0] != 0 and (stockFuturePrice['lowestPrice'].values[0] - stockBuyPrice)/stockBuyPrice <= down_Limit:
				stock_Selected.ix[stock_Selected['secID']==stock, 'Exit_Status'] = -1
				stock_Selected.ix[stock_Selected['secID']==stock, 'Hold_Days'] = hold_DayCount - Future_Gap
				stock_Selected.ix[stock_Selected['secID']==stock, 'Exit_Date'] = stockFuturePrice['tradeDate'].values[0]
				break
			elif hold_DayCount - Future_Gap >= hold_Limit:
				stock_Selected.ix[stock_Selected['secID']==stock, 'Exit_Status'] = 0
				stock_Selected.ix[stock_Selected['secID']==stock, 'Hold_Days'] = hold_DayCount - Future_Gap
				stock_Selected.ix[stock_Selected['secID']==stock, 'Exit_Date'] = stockFuturePrice['tradeDate'].values[0]
				break
			else:
				stockFuturePrice = DataAPI.MktEqudGet(secID=stock,ticker=u"",tradeDate=cal.advanceDate(Date.parseISO(stockFuturePrice['tradeDate'].values[0]), Period('1D'), BizDayConvention.Following).strftime('%Y%m%d'),beginDate=u"",endDate=u"",field=u"tradeDate,highestPrice,lowestPrice,accumAdjFactor",pandas="1")
				hold_DayCount += 1
		stockAvgPrice = DataAPI.MktEqudGet(secID=stock,ticker=u"",tradeDate=Date.parseISO(stockFuturePrice['tradeDate'].values[0]).strftime('%Y%m%d'),beginDate=u"",endDate=u"",field=u"tradeDate,closePrice,accumAdjFactor",pandas="1")
		stockAvgPrice['closePrice'] = stockAvgPrice['closePrice'] * stockAvgPrice['accumAdjFactor']
		avg_Gain = (stockAvgPrice['closePrice'].values[0] - stockBuyPrice)/stockBuyPrice
		stock_Selected.ix[stock_Selected['secID']==stock, 'avg_Gain'] = avg_Gain

stock_Selected.ix[stock_Selected['Exit_Status']==1, 'avg_Gain'] = up_Limit
stock_Selected.ix[stock_Selected['Exit_Status']==-1, 'avg_Gain'] = down_Limit
Expectation = stock_Selected[~np.isnan(stock_Selected['avg_Gain'])]['avg_Gain'].values.mean()

print('Our Expectation is: ' + str(Expectation))
stock_Selected
