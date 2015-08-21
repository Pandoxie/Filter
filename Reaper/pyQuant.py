import numpy as np
def isBuyingTime(macd, closePrices, tradeTiming, bandwidth, recentwidth, barGap):
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