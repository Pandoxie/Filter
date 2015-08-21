# -*- coding: utf-8 -*-
# 1, Obtain 'selected_Sec_List' according to certian rules
# 2, Get all 'market_Data' within date range
# 3, Obtain section composition 'section_Info'
# 4, Compute section daily change index 'section_Data'
# 5, Compute section total avg_Chang store back to 'selected_Sec_List'
import talib as tb
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import pandas as pd
import CAL.PyCAL as cal

Stock_ID = 101001002 #Stock Classification ID
start_Date = cal.Date(2015,5,1)
end_Date = cal.Date(2015,6,1)
fields = ['secID','secShortName','tradeDate','preClosePrice','openPrice','highestPrice','lowestPrice','closePrice','turnoverRate','marketValue']

biz_cal = cal.Calendar('CHINA.SSE')
def isFirstDigits(num, pattern=Stock_ID):
	if str(num)[:len(str(pattern))] == str(pattern):
		return True
	else:
		return False

def addOne(num):
	if not np.isnan(num):
		return num + 1
	else:
		return np.nan

def GetMktInfo(secID, beginDate, endDate, field):
	num = 50
	count_num = len(secID)/num
	if count_num>0:
		MktInfo_df = DataFrame({})
		for i in range(count_num):
			sub_info = DataAPI.MktEqudGet(secID=secID[i*num:(i+1)*num],beginDate=beginDate,endDate=endDate,field=field)
			MktInfo_df = pd.concat([MktInfo_df,sub_info])
		sub_info = DataAPI.MktEqudGet(secID=secID[(i+1)*num:],beginDate=beginDate,endDate=endDate,field=field)
		MktInfo_df = pd.concat([MktInfo_df,sub_info])
	else:
		MktInfo_df = DataAPI.MktEqudGet(secID=secID,beginDate=beginDate,endDate=endDate,field=field)
	return MktInfo_df

wholeSecList =DataAPI.SecTypeGet(field=u"",pandas="1") #All Types
selected_Sec_List = wholeSecList[(wholeSecList['typeLevel']==6) & (wholeSecList['typeID'].map(isFirstDigits))] #Filter Stocks of certain type

market_Data = pd.DataFrame({})
#Obtain all Market Transaction Data from Start to End
for date in biz_cal.bizDatesList(start_Date, end_Date):
	market_Data = market_Data.append(DataAPI.MktEqudGet(secID=u"",ticker=u"",tradeDate=date.strftime('%Y%m%d'),beginDate=u"",endDate=u"",field=fields,pandas="1"), ignore_index= True)

#Get maps between sections and stocks
section_Info = pd.DataFrame({})
for section in selected_Sec_List['typeID']:
	try:
		section_Info = section_Info.append(DataAPI.SecTypeRelGet(typeID=section,secID=u"",ticker=u"",field=u"",pandas="1"), ignore_index= True)
	except :
		print('No stock in: ' + selected_Sec_List.loc[selected_Sec_List.typeID==section, 'typeName'].values[0])

#Compute sections change rate with time
section_Data = pd.DataFrame({})
for date in biz_cal.bizDatesList(start_Date, end_Date):
	for section in selected_Sec_List['typeID']:
		stocks_in_section = list(section_Info.loc[section_Info.typeID==section, 'secID'].values)
		if stocks_in_section:
			sect_market_Data = market_Data[(market_Data.secID.isin(stocks_in_section)) & (market_Data.tradeDate == date.toISO())]
			if len(sect_market_Data) != 0:
				sect_market_Data['inc_rate'] = (sect_market_Data['closePrice'] - sect_market_Data['preClosePrice'])/sect_market_Data['preClosePrice']
				ind_inc = (sect_market_Data['inc_rate'] * sect_market_Data['marketValue']).sum()/sect_market_Data['marketValue'].sum()
				section_Data = section_Data.append(pd.DataFrame({'tradeDate':date.toISO(), 'typeID':section, 'typeName':selected_Sec_List.loc[selected_Sec_List.typeID==section, 'typeName'].values[0], 'ChangeIdx':ind_inc}, index = [1]), ignore_index= True)

selected_Sec_List['avg_Chang'] = np.nan
for section in selected_Sec_List['typeID']:
	if list(section_Info.loc[section_Info.typeID==section, 'secID'].values):
		selected_Sec_List.loc[selected_Sec_List.typeID==section, 'avg_Chang'] = section_Data.loc[section_Data.typeID==section, 'ChangeIdx'].map(addOne).prod()

selected_Sec_List.sort(columns='avg_Chang', ascending=False)

section_Data.to_csv('section_Data-' + start_Date.toISO() + '-' + end_Date.toISO() + '.csv', encoding='utf-8')
market_Data.to_csv('market_Data-' + start_Date.toISO() + '-' + end_Date.toISO() + '.csv', encoding='utf-8')
section_Info.to_csv('section_Info-' + start_Date.toISO() + '-' + end_Date.toISO() + '.csv', encoding='utf-8')
selected_Sec_List.to_csv('selected_Sec_List-' + start_Date.toISO() + '-' + end_Date.toISO() + '.csv', encoding='utf-8')
