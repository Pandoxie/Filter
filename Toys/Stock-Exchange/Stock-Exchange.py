# -*- coding: utf-8 -*-
# 1, Obtain 'ExchangeRate'
# 2, Subtract SZZS 'inc_rate' from Section 'ChangeIdx'
# 3, Get corr from columns of 'section_Exchange_co_trend'
import talib as tb
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import pandas as pd
import CAL.PyCAL as cal

start_Date = cal.Date(2014,10,1)
end_Date = cal.Date(2015,4 ,1)


section_Data = pd.read_csv('section_Data-' + start_Date.toISO() + '-' + end_Date.toISO() + '.csv', encoding='utf-8', parse_dates=True, index_col='tradeDate', usecols=['tradeDate','typeID','typeName','ChangeIdx'])
market_Data = pd.read_csv('market_Data-' + start_Date.toISO() + '-' + end_Date.toISO() + '.csv', encoding='utf-8', parse_dates=True, index_col='tradeDate', usecols=['secID', 'secShortName', 'tradeDate', 'preClosePrice', 'openPrice', 'highestPrice', 'lowestPrice', 'closePrice', 'turnoverRate', 'marketValue'])
section_Info = pd.read_csv('section_Info-' + start_Date.toISO() + '-' + end_Date.toISO() + '.csv', encoding='utf-8', parse_dates=True, index_col='typeID', usecols=['typeID', 'typeName', 'secID', 'ticker', 'exchangeCD', 'secShortName'])
selected_Sec_List = pd.read_csv('selected_Sec_List-' + start_Date.toISO() + '-' + end_Date.toISO() + '.csv', encoding='utf-8', parse_dates=True, index_col='typeID', usecols=['typeID', 'typeName', 'parentID', 'typeLevel', 'avg_Chang'])

ExchangeRate = DataAPI.ChinaDataExchangeRateGet(indicID=u"M110000003",indicName=u"",beginDate=start_Date.strftime('%Y%m%d'),endDate=end_Date.strftime('%Y%m%d'),field=u"",pandas="1")[['periodDate','dataValue']]
ExchangeRate = ExchangeRate.rename(index = pd.to_datetime(ExchangeRate['periodDate']))['dataValue']

SZZS = DataAPI.MktIdxdGet(indexID=u"000001.ZICN",ticker=u"",tradeDate=u"",beginDate=start_Date.strftime('%Y%m%d'),endDate=end_Date.strftime('%Y%m%d'),field=u"",pandas="1")
SZZS['inc_rate'] = (SZZS['closeIndex'] - SZZS['preCloseIndex'])/SZZS['preCloseIndex']
SZZS = SZZS.rename(index = pd.to_datetime(SZZS['tradeDate']))

section_Exchange_co_trend = pd.DataFrame({})
section_Exchange_co_trend['USD2RMB_Exchange'] = ExchangeRate
for section in selected_Sec_List.index.values:
	section_Exchange_co_trend[selected_Sec_List.ix[section].typeName] = section_Data.loc[section_Data.typeID==section, 'ChangeIdx'] - SZZS['inc_rate']

pd.DataFrame(section_Exchange_co_trend.corr()['USD2RMB_Exchange'].order())
