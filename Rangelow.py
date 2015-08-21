import talib as tb
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import pandas import pd
from CAL.PyCAL import *

start_date = Date(2015, 8, 15)
end_date = Date(2015, 8, 19)
top_List = 50


cal = Calendar('CHINA.SSE')
start_date = cal.advanceDate(start_date, Period('0D'), BizDayConvention.Preceding)
end_date = cal.advanceDate(end_date, Period('0D'), BizDayConvention.Preceding)
#ctime = dt.datetime.now().time().strftime('%H:%M')

if end_date == Date.todaysDate():
	ctime = DataAPI.MktBarRTIntraDayGet(securityID=u"000001.XSHE",pandas="1")['barTime'].iloc[-1]
	StockSnapShot = DataAPI.BarRTIntraDayOneMinuteGet(time=ctime,field="ticker,shortNM,closePrice",pandas="1")
	StockSnapShot = StockSnapShot.rename(index = StockSnapShot['ticker']+'.'+StockSnapShot['exchangeCD']).loc[:,['shortNM', 'closePrice']]
	StockSnapShot = StockSnapShot[StockSnapShot['closePrice']!=0]
else:
	StockSnapShot = DataAPI.MktEqudGet(secID=u"",ticker=u"",tradeDate=end_date.strftime('%Y%m%d'),beginDate=u"",endDate=u"",field=u"",pandas="1")
	StockSnapShot = StockSnapShot[StockSnapShot['highestPrice']!=0]
	StockSnapShot['closePrice'] = StockSnapShot['closePrice'] * StockSnapShot['accumAdjFactor']
	StockSnapShot = StockSnapShot.rename(index = StockSnapShot['secID'], columns={'secShortName':'shortNM'}).loc[:,['shortNM', 'closePrice']]


StockSnapShot['Price_Change'] = np.nan
StockSnapShot['New_Low'] = False
StockSnapShot['Possible_New_Low'] = False

for stock in StockSnapShot.index.values:
	try:
		stockHistPrice = DataAPI.MktEqudGet(secID=stock,ticker=u"",tradeDate=u"",beginDate=start_date.strftime('%Y%m%d'),endDate=cal.advanceDate(end_date, Period('-1D'), BizDayConvention.Preceding).strftime('%Y%m%d'),field=u"tradeDate,highestPrice,closePrice,accumAdjFactor",pandas="1")
	except:
		continue
	stockHistPrice['closePrice'] = stockHistPrice['closePrice'] * stockHistPrice['accumAdjFactor']
	stockHistPrice = stockHistPrice[stockHistPrice['highestPrice'] != 0]
	stockHistHigh = stockHistPrice.ix[[Date.parseISO(x) >= start_date for x in stockHistPrice['tradeDate'].values], 'closePrice'].max()
	stockHistLow = stockHistPrice.ix[[Date.parseISO(x) >= start_date for x in stockHistPrice['tradeDate'].values], 'closePrice'].min()
	stockNowPrice = StockSnapShot.loc[stock]['closePrice']
	stockChange = (stockNowPrice - stockHistHigh)/stockHistHigh
	StockSnapShot.loc[stock, 'Price_Change'] = stockChange
	if stockNowPrice <= stockHistLow:
		StockSnapShot.loc[stock, 'New_Low'] = True
	elif stockHistLow/stockNowPrice >= 0.9:
		StockSnapShot.loc[stock, 'Possible_New_Low'] = True

stock_Selected = StockSnapShot.sort(columns='Price_Change', ascending=True).head(top_List)
stock_Selected.to_csv('RangeLow_Selected.csv', encoding='utf-8')
