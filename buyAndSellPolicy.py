import baostock as bs
import pandas as pd
import openpyxl
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
from func import *






def getMacdTrend(i,df,value,trend):
    # 识别当前点的DEA是向上或向下
    for x in range(1000):
        if i >= x:
            value2 = df.at[i - x, value] #基于当前i行，不断向前找H/L,找到就更新当前行

            # # # 处理bar值的周期排序（每个波动周期重新排序）
            # if value2 == 'H' or value2 == 'L':
            #     if x > 0:
            #         array = []
            #         value = getValueRank(i, df, 'bar', 'barRankPeriod', array, x,'middle')
            #         df = value[0]

            if value2 == 'H':
                if x < 4:
                    df.at[i, trend] = '向下,刚过H点'
                else:
                    df.at[i, trend] = '向下'
                break
            if value2 == 'L':
                if x < 4:
                    df.at[i, trend] = '向上,刚过L点'
                else:
                    df.at[i, trend] = '向上'
                break


        else:
            break
    return df


#取半年内bar值排名的百分比
def getValueRank2(i,df,value,rank,array,row):
    # 把之前125行bar值写入数组，之后就出一个入一个
    bar = df.at[i,value]
    if i < row + 10 and i > 10:
        row = i
        arrayTemp = []
        for x in range(row):
            test = df.at[i-x, value]
            arrayTemp.append(test)
        # df.at[i,'barArray'] = arrayTemp
        array = arrayTemp
    if i + 10 >= row + 10:
        array.pop() #删除最后一个元素
        array.insert(0,bar)
        # df.at[i, 'barArray'] = array
        # print(array)
        temp = array[:]
        temp.sort()
        if bar >= 0:
            #当为正数
            arr = np.array(temp)
            temp = arr[arr >= 0] #
            temp = temp.tolist()
            index = temp.index(abs(bar))
            rankPrecent = (index + 1) / len(temp)
        else:
            #当为负数
            arr = np.array(temp)
            temp = arr[arr < 0] #仅取负值
            temp = temp.tolist()
            temp.reverse() #倒排
            for x in range(len(temp)):
                temp[x] = abs(temp[x])
            index = temp.index(abs(bar))
            rankPrecent = - (index + 1)/len(temp)
        #标记当当天的bar在bar数组是在什么位置，前20%？
        df.at[i, rank] = format(rankPrecent,'.2%')
    return [df, array]





#取dea、dif曲线的趋势
def getDeaDifTrend(i,df,value,trend):
    temp = df.at[i,value]
    if temp == 'H':
        x = 0
        while df.at[i+x,value] != 'L' and i+x < len(df)-1:
            if x < 4:
                df.at[i+x, trend] = '向下,刚过H点'
            else:
                df.at[i+x, trend] = '向下'

            #取本周内bar值排序,
            array = []
            m = x + 1
            df = getValueRank(i+x, df, 'bar', 'barRankPeriod', array, m,'middle')[0]
            x += 1

    if temp == 'L':
        x = 0
        while df.at[i+x,value] != 'H'and i+x < len(df)-1:
            if x < 2:
                df.at[i+x, trend] = '向上,刚过L点'
            else:
                df.at[i+x, trend] = '向上'

            #取本周内bar值排序,
            array = []
            m = x + 1
            df = getValueRank(i+x, df, 'bar', 'barRankPeriod', array, m,'middle')[0]
            x += 1

    return df


#从开始或中间取数值排序
def getValueRankFrom(i,df,value,array,row,label):
    if 'start' == label:
        bar = df.at[i, value]
        if i <= row:  # 为了减少循环次数，当i>row就不全部循环取值，而是在i=row的数组基础上推出一个，添加一个。。当这个前提逻辑，i一定要从0或1开始，以保证数据完整
            arrayTemp = []
            for x in range(i):
                test = df.at[i - x, value]
                arrayTemp.append(test)
            array = arrayTemp
        else:
            array.pop()  # 删除最后一个元素
            array.insert(0, bar)
        return array

    if 'middle' == label:
        if i <= row:
            row = i
        arrayTemp = []
        for x in range(row):
            test = df.at[i - x, value]
            arrayTemp.append(test)
        array = arrayTemp
        return array


def getValueRank(i,df,value,rank,array,row,label):
    # 把之前125行bar值写入数组，之后就出一个入一个
    bar = df.at[i,value]
    if i > 0:
        array = getValueRankFrom(i,df,value,array,row,label)

        #处理排序
        temp = array[:] #在新地址复制array
        temp.sort()
        if bar >= 0:
            #当为正数
            arr = np.array(temp)
            temp = arr[arr >= 0] #取正数
            temp = temp.tolist()
            # print(i)
            index = temp.index(abs(bar))
            rankPrecent = (index + 1) / len(temp)
        else:
            #当为负数
            arr = np.array(temp)
            temp = arr[arr < 0] #仅取负值
            temp = temp.tolist()
            temp.reverse() #倒排
            for x in range(len(temp)):
                temp[x] = abs(temp[x])
            index = temp.index(abs(bar))
            rankPrecent = - (index + 1)/len(temp)
        #标记当当天的bar在bar数组是在什么位置，前20%？
        df.at[i, rank] = format(rankPrecent,'.2%')
        rr = df.at[i, rank]
        tes = 1
    return [df, array]


# def getValueRank_bak(i,df,value,rank,array,row):
#     # 把之前125行bar值写入数组，之后就出一个入一个
#     bar = df.at[i,value]
#     if i < row and i > 0:
#     # if i < row and i > 10:
#         row = i
#         arrayTemp = []
#         for x in range(row):
#             test = df.at[i-x, value]
#             arrayTemp.append(test)
#         # df.at[i,'barArray'] = arrayTemp
#         array = arrayTemp
#     if i >= row:
#         array.pop() #删除最后一个元素
#         array.insert(0,bar)
#         # df.at[i, 'barArray'] = array
#         # print(array)
#         temp = array[:]
#         temp.sort()
#         if bar >= 0:
#             #当为正数
#             arr = np.array(temp)
#             temp = arr[arr >= 0] #
#             temp = temp.tolist()
#             index = temp.index(abs(bar))
#             rankPrecent = (index + 1) / len(temp)
#         else:
#             #当为负数
#             arr = np.array(temp)
#             temp = arr[arr < 0] #仅取负值
#             temp = temp.tolist()
#             temp.reverse() #倒排
#             for x in range(len(temp)):
#                 temp[x] = abs(temp[x])
#             index = temp.index(abs(bar))
#             rankPrecent = - (index + 1)/len(temp)
#         #标记当当天的bar在bar数组是在什么位置，前20%？
#         df.at[i, rank] = format(rankPrecent,'.2%')
#     return [df, array]







# 策略：用日macd的向下，向下趋势来判断买卖，重点是bar值方向
def buyPolicyMacdTrend(i, df):

    # 做判断，基于bar+dea来做买入卖出判断
    # 买入判断：
    # 1）dea向下、当天bar值排名30%内，明天买考虑买入（收盘价左右）
    # 2）去掉短期波动：如果在一个周期内（现在到上一个H点），bar值没有达到过50%，就不买
    # 3）出现买入信号，第二日收盘价买入

    # 卖出判断：
    # 1)dea向上，bar值在长时间排名30%，或本周期排名30%内，明天考虑卖出
    # 2）当前卖出点向上找L点，如果barRank没有出现50%，就不卖
    # 2）出现卖出信号，第二日收盘价卖出

    # 问题：由于修改买入标志，卖出就更近，有问题。

    # 买入判断：从数据开始的6个月后开始买入
    if i > 125:
        barRank = str2Float(df.at[i, 'barRank'])
        deaTrend = df.at[i, 'deaTrend']
        if barRank < 0.3:
            # if barRank < 0.3 or barRankPeriod < 0.3:
            if deaTrend == '向下' or deaTrend == '向上,刚过L点':
                df.at[i, 'buy'] = 'dea明天买入'

                # 向上找最近一个H点，统计当前到H点这段时间点bar值，如果没有超过50%，就表明不适合买入
                for x in range(1000):
                    deaHL = df.at[i - x, 'deaHL']
                    if deaHL == 'H':
                        break
                    barRankTemp = df.at[i - x, 'barRank']
                    if str2Float(barRankTemp) > 0.5:
                        df.at[i, 'buy2'] = 'dea买入(去波动)'

        # 卖出判断：dea向上，bar值在长时间排名30%，或本周期排名30%内，明天考虑卖出。
        # 找本周期到起点L（最近到L)
        if deaTrend == '向上':
            barRankPeriod = str2Float(df.at[i, 'barRankPeriod'])
            key = 0
            if barRank < 0.3 or barRankPeriod < 0.3:
                x = 0
                while df.at[i - x, 'deaHL'] != 'L':  # 当前卖出点向上找L点，如果barRank没有出现50%，就不卖
                    if str2Float(df.at[i - x, 'barRank']) > 0.5:
                        key = 1
                    x += 1
            if barRank < 0.3 and key == 1:
                df.at[i, 'sell'] = 'dea卖出'
            if barRankPeriod < 0.3 and key == 1:
                df.at[i, 'sell2'] = 'dea卖出（短周期)'
    return df




#策略：收盘价出现两次双向下后，第一次出现双向上就买入
def buyPolicy1(df, buyState, buycount, buyIndex, buyPrice, i):
    if df.at[i, 'ma5动态'] == '' and df.at[i, 'ma10动态'] == '':
        df.at[i, '双向下'] = 1
    if df.at[i, 'ma双向上价K线内'] == 'Y' and buyState == 0:  # 从当前"双向上"行，找上一个"双向上"行，然后计算"双向下"的数量，大于等于2，就把本行设为买点
        x = 0
        for j in range(1, 100):
            if df.at[i - j, '双向下'] == 1:
                x = x + 1
            if df.at[i - j, '双向上'] != '':
                break
        # 检查macd是否合适买入
        if x >= 2:
            df.at[i, '买入点'] = 1
            buyIndex = i
            buyState = 1
            buycount = buycount + 1
            buyPrice = df.at[i, 'ma双向上价']
            df.at[i, '买入价'] = buyPrice
            df.at[i, 'macd检查'] = checkMacd(i, df)[0]
            df.at[i, 'macd检查说明'] = checkMacd(i, df)[1]

    # 买入后，刷新买入价与每天高低价的比较
    if buyState == 1:
        df.at[i, '最低价/买入'] = format(df.at[i, 'low'] / buyPrice - 1, '.2%')
        df.at[i, '最高价/买入'] = format(df.at[i, 'high'] / buyPrice - 1, '.2%')

    return [df, buyState, buycount, buyIndex, buyPrice]



#####上面是买策略，下面是卖策略####
def sellPolicy1(df, buyState, buyPrice, buyIndex, lossPrecent, winPrecent, losscount, wincount, lossReduce, winReduce, i):
    if buyState == 1 and df.at[i, '买入点'] != 1:
        lossPrice = buyPrice * (1 - lossPrecent)
        winPrice = buyPrice * (1 + winPrecent)
        if df.at[i, 'low'] < lossPrice:
            df.at[buyIndex, '是否盈利'] = 0
            df.at[i, '卖出价'] = lossPrice
            buyState = 0
            losscount = losscount + 1
            if df.at[buyIndex, "macd检查"] == 0:
                lossReduce = lossReduce + 1

        if df.at[i, 'high'] > winPrice:
            df.at[buyIndex, '是否盈利'] = 1
            df.at[i, '卖出价'] = winPrice
            buyState = 0
            wincount = wincount + 1
            if df.at[buyIndex, "macd检查"] == 0:
                winReduce = winReduce + 1

        if df.at[i, 'low'] < lossPrice and df.at[i, 'high'] > winPrice:
            df.at[buyIndex, '是否盈利'] = '不确定'
            buyState = 0
    return [df, buyState, buyPrice, buyIndex, lossPrecent, winPrecent, losscount, wincount, lossReduce, winReduce]


#####上面是卖策略，下面是策略相关公共组件######



#检查一下macd这个点是否靠谱
def checkMacd(i,dfSource):

    #用基线买入价来计算此时刻的macd, 这个主要用来判断此刻买入是否合适
    df = dfSource.copy() #避免修改df的原来值，用copy方法可以复制一份，不修改原值
    closePriceUpup = df.at[i,'ma双向上价']
    previousEMA12 = df.at[i-1,'ema12']
    previousEMA26 = df.at[i-1,'ema26']
    previousDEA = df.at[i-1,'macd_dea']



    macdUpup = getMacd(df.at[i-1,'ema12'], df.at[i-1,'ema26'], df.at[i-1,'macd_dea'], closePriceUpup)
    #用这这个基线价计算出来的macd来做判断，临时更新一个df（但不修改导出数据，导出数据还是用当天收盘价来计算）
    df.at[i,'macd_dif'] = macdUpup[0]
    df.at[i, 'macd_dea'] = macdUpup[1]
    df.at[i,'macd_macd'] = macdUpup[2]

    difArray = []
    deaArray = []
    difTrend = 0.1
    deaTrend = 0.1
    dif = df.at[i,'macd_dif']
    dea = df.at[i,'macd_dea']
    buyKey = 1
    buyDesc = ''

    #判断均线的斜率趋势，先用最近5天数据看看//    #判断macd的趋势方法，参考文章：https://zhuanlan.zhihu.com/p/112703276
    difArrayTemp = []
    deaArrayTemp = []
    for j in range(0,5):
        a = df.at[i - j, 'macd_dif']
        b = df.at[i - j, 'macd_dea']
        difArrayTemp.append(a)
        deaArrayTemp.append(b)
    difArrayTemp.reverse()
    deaArrayTemp.reverse()
    difTrend = trendline(difArrayTemp)
    deaTrend = trendline(deaArrayTemp)


    if difTrend < 0 and deaTrend < 0:
        buyKey = 0
        buyDesc = '两线趋势向下，不适合买入' + '; macd数据：' + str(round(macdUpup[0],4)) + ', ' + str(round(macdUpup[1],4)) + ', ' + str(round(macdUpup[2],4) )

    if deaTrend < 0 and difTrend > 0:
        buyKey = 1
        buyDesc = '慢线向下，快线向上，考虑买入' +  '; macd数据：' + str(round(macdUpup[0],4)) + ', ' + str(round(macdUpup[1],4)) + ', ' + str(round(macdUpup[2],4) )

    #若当天是dif是正数，向左边取每天的dif值，直到0， 然后从这些天取到：最大值，平均值，当天值与这两值到偏差
    if dif > 0:
        for j in range(0,1000):
            if i - j == 0:
                break
            difPrevious = df.at[i - j, 'macd_dif']
            if difPrevious < 0:
                break
            difArray.append(difPrevious)


        # difArray = np.array(difArray)
        # difMax = difArray.max(axis=0) #最大值
        # difMin = difArray.min(axis=0) #最小值
        # difAvg = difArray.mean() #平均值
        # difMiddle = np.median(difArray) #中间值
        #



    if dea > 0:
        for j in range(0,1000):
            if i - j == 0:
                break
            deaPrevious = df.at[i - j, 'macd_dea']
            if deaPrevious < 0:
                break
            deaArray.append(deaPrevious)

        # deaArray = np.array(deaArray)
        # deaMax = deaArray.max(axis=0) #最大值
        # deaMin = deaArray.min(axis=0) #最小值
        # deaAvg = deaArray.mean() #平均值
        # deaMiddle = np.median(deaArray) #中间值
        #
        # if dea < deaMax and dea > deaAvg:
        #     buyKey = 'dea正值高位，不适合买入'
    return [buyKey,buyDesc]



#获取某个时刻股价的macd
def getMacd(previousEMA12,previousEMA26,previousDEA,closePrice):
    EMA12 = getEMA(12,previousEMA12,closePrice)
    EMA26 = getEMA(26,previousEMA26,closePrice)
    dif = EMA12 - EMA26
    dea = getEMA(9,previousDEA,dif)
    macdBar = 2*(dif-dea)
    return [dif,dea,macdBar]


def getEMA(number,EMAprevious, closePrice):
    EMA = EMAprevious * (number-1) / (number+1) + closePrice * 2 / (number+1)
    return EMA


def trendline(data):
    order=1
    index=[i for i in range(1,len(data)+1)]
    coeffs = np.polyfit(index, list(data), order)
    slope = coeffs[-2]
    return float(slope)