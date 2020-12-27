import baostock as bs
import pandas as pd
import openpyxl
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
from func import *
from buyAndSellPolicy import *
from doubleKlineMethod import *
import time



pd.set_option('display.width',210)
pd.set_option('display.max_columns',130)
pd.set_option('display.max_colwidth',130)
pd.set_option('display.max_rows', None)

#策略测试
def checkPolicy(stockCodeArray,toFile,stockNameArray):

    # tis1 = time.perf_counter()
    #
    # tis2 = time.perf_counter()
    # print(tis2 - tis1)
    #有时在这测试代码#


    #拆分checkPolicy处理后csv大文件，然后按股票代码生成单个csv文件
    if toFile == 2:
        df = pd.read_csv('/Users/miketam/Downloads/checkPolicy_300.csv', sep=',',encoding="gb2312")
        # df = pd.read_csv('/Users/miketam/Downloads/getOnlyKline.csv', header=None, sep=',')
        dfArray = dfDivide(stockCodeArray, df)
        dfArrayNew = []
        rank = 0.4 #barRank排名百分比
        x = 0
        for df in dfArray:
            # if abs(str2Float(df.at[-2,'barRank'])) < 0.4 or abs(str2Float(df.at[-3,'barRank']))< 0.4 or abs(str2Float(df.at[-4,'barRank'])) < 0.4:
            if abs(str2Float(df.iloc[-2]['barRank'])) < rank or abs(str2Float(df.iloc[-3]['barRank']))< rank:
                # print(df[['date', 'close', '增幅', 'ma10', 'Cma10', 'ma5动态', 'ma10动态', '双向上', 'barRank', 'barRankPeriod','deaHL', 'deaTrend', 'deaPRank', 'deaGTS', 'deaGPRank', 'buy2', 'sell', 'sell2']])
                df = df[['code','date', 'close', '增幅', 'ma10', 'Cma10', 'ma5动态', 'ma10动态', '双向上', 'barRank', 'barRankPeriod','deaHL', 'deaTrend', 'deaPRank', 'deaGTS', 'deaGPRank', 'buy2', 'sell', 'sell2']]
                code = df.iloc[-2]['code']
                stockName = stockNameArray[x]
                url = '/Users/miketam/Downloads/checkPolicy/'+ code + '.csv'
                urlXlsx = '/Users/miketam/Downloads/checkPolicy/'+ stockName + '_' + code + '.xlsx'
                # df.to_csv(url, encoding="gbk", index=False)
                df.to_excel(urlXlsx, float_format='%.5f', index=False)
                dfArrayNew.append(df)
            x = x + 1
        return dfArrayNew


    #根据策略处理数据


    dfKline = processKline(stockCodeArray, toFile=toFile)


    dfday = dfKline[0] #取日线数据
    dfweek = dfKline[1] #取周线数据
    dfDayArray = dfDivide(stockCodeArray,dfday) #把df拆分，每个股票一个df
    dfweekArray = dfDivide(stockCodeArray,dfweek) #把df拆分，每个股票一个df

    resultArray = []
    dfAppend: DataFrame = pd.DataFrame()

    #处理每一个股票的df
    for x in range(len(dfDayArray)):
        df = dfDayArray[x]
        dfweek = dfweekArray[x]

        #计算周数据在日表到列位置 （方便后续引用）
        weekDataBegin = df.shape[1]
        weekDataEnd = weekDataBegin + dfweek.shape[1]

        #在日线表创建周线表到列
        columnNameList = list(dfweek)
        for l in columnNameList:
            nameNew = l + '_W'
            dfweek.rename(columns={l: nameNew}, inplace=True) #给周线表列表增加'_w'标记，以示区分
            df[nameNew] = dfweek.at[0,nameNew]  # 在日线df增加周线df的列
        columnNameList = list(dfweek)


        #为提升效率，用list处理dfweek日期
        week = dfweek.iloc[:,0].values
        week2 = []
        for we in week:
            week2.append(getYearWeekFromDate(we))
        week = week2



        # print(list(df))
        # exit()
        code = ''
        # df['双向下'] = ''
        # df['买入点'] = ''
        # df['买入价'] = ''
        # df['最低价/买入'] = ''
        # df['最高价/买入'] = ''
        # df['卖出价'] = ''
        # df['是否盈利'] = ''
        # df['macd检查'] = ''
        # df['macd检查说明'] = ''

        # df['barArray'] = ''
        # df['barRank'] = ''
        # df['deaTrend'] = ''


        buyIndex = 0
        buyState = 0
        buyPrice = 0
        buycount = 0
        wincount = 0
        winReduce = 0   #根据macd减少盈利次数
        losscount = 0
        lossReduce = 0  #根据macd减少损失次数
        winPrecent = 0.04
        lossPrecent = 0.04
        array = []
        array2 = []
        array3 = []
        array4 = []


        index = len(df) - 1 #得到索引,减1是因为之前增加一个不规则的行数据
        barHLidList = df.loc[(df.barHL == 'H') | (df.barHL == 'L')].index.tolist() #bar所有HL点的的行的索引

        #这个循环效率，日后可以优化

        for i in range(index):
            code = df.at[0,'code']


            # #估计bar值所在波形的位置
            df = getBarPositionDf(barHLidList,df,i)  #里面的describe函数很慢


            #识别当前点的DEA、dif是向上或向下
            # df = getMacdTrend(i,df,'deaHL','deaTrend')
            # df = getMacdTrend(i,df,'difHL','difTrend')
            df = getDeaDifTrend(i,df,'deaHL','deaTrend') #里面rank值是本周期内(bar值周期内排序在里面）
            # df = getDeaDifTrend(i,df,'difHL','difTrend')


            #处理bar值的半年排序
            value = getValueRank(i,df,'bar','barRank',array,250,'start')
            df = value[0]
            array =value[1]

            # 处理dea/Price的排序
            value = getValueRank(i,df,'deaP','deaPRank',array3, 250,'start')
            df = value[0]
            array3 =value[1]


            #处理deaGrowth/Price的排序
            value = getValueRank(i,df,'deaGP','deaGPRank',array2, 250,'start')
            df = value[0]
            array2 =value[1]



            #处理deaGrowth/Price的排序
            value = getValueRank(i,df,'dea','deaRank',array2, 250,'start')
            df = value[0]
            array4 =value[1]

            #识别dea增量趋势、dif增量趋势
            temp = []
            if i > 2:
                for x in range(-2,1):
                    temp.append(abs(df.at[i+x,'deaGrowth']))
                df.at[i, 'deaGrowthTrend'] = trendline(temp)
                if trendline(temp) > 0:
                    df.at[i, 'deaGTS'] = '加速'
                else:
                    df.at[i, 'deaGTS'] = ''

            temp = []
            if i > 2:
                for x in range(-2,1):
                    temp.append(abs(df.at[i+x,'difGrowth']))
                df.at[i, 'difGrowthTrend'] = trendline(temp)
                if trendline(temp) > 0:
                    df.at[i, 'difGTS'] = '加速'
                else:
                    df.at[i, 'difGTS'] = ''


            # 把周线数据写入日线列表
                #找到当前日线对应的周线，把数据复制过去
            dayYearWeek = getYearWeekFromDate(df.iat[i,0]) #找到某天对应到年份+周数
            if dayYearWeek in week:
                p = week.index(dayYearWeek)
                # df.loc[i, columnNameList[0]:columnNameList[len(columnNameList) - 1]] = dfweek.iloc[p]
                df.iloc[i, weekDataBegin:weekDataEnd] = dfweek.iloc[p]  #上行也可以，差别只是定位方式不一样


            #买策略：利用macd到dea和bar的高点变化来给出买点
            df = buyPolicyMacdTrend(i, df)

            #买策略：用kdj、ma100、日macd趋势、周macd趋势来识别买点


            #买入策略：利用ma双向上来判断
            # buy = buyPolicy1(df, buyState, buycount, buyIndex, buyPrice, i)
            # df = buy[0]
            # buyState = buy[1]
            # buycount = buy[2]
            # buyIndex = buy[3]
            # buyPrice = buy[4]


            # #卖出策略1
            # sell = sellPolicy1(df, buyState, buyPrice, buyIndex, lossPrecent, winPrecent, losscount, wincount, lossReduce, winReduce,i)
            # df = sell[0]
            # buyState = sell[1]
            # buyPrice = sell[2]
            # # buyIndex = sell[3]
            # lossPrecent = sell[4]
            # winPrecent = sell[5]
            # losscount = sell[6]
            # wincount = sell[7]
            # lossReduce = sell[8]
            # winReduce = sell[9]


        # print(list(df))
        # print(df.head())

        resultStr = '股票：' +code + '，购买次数：' + str(buycount)  + "，盈利次数：" + str(wincount) + "，亏损次数：" + str(losscount),'因macd少盈利：' + str(winReduce) +\
                 ', 因macd少亏损：' + str(lossReduce) + ', 实际盈利：'+ str(wincount-winReduce) + ', 实际亏损：' + str(losscount - lossReduce)
        resultArray.append(resultStr)
        dfAppend = dfAppend.append(df)

        # print(df[['date','bar','barRank','deaHL','deaTrend','difHL','difTrend']])
        # print(df[['date','bar','barRank','deaHL','dea','deaTrend','deaGrowthTrend','deaGrowthTrendSign','deaGP','deaGPRank','deaPRank']])
        # print(df[['date','close','bar','barRank','barRankPeriod','deaHL','deaTrend','difHL','difTrend','difGrowthTrend','difGrowthTrendSign','deaGP','deaGPRank','deaPRank','buy','buy2','sell','sell2']])
        # print(df[['date','bar','barRank','deaHL','deaTrend','difHL','difTrend','difGrowth','difGP','deaGrowth','deaGrowthTrend','deaGP']])

        # print(df[['date','close','增幅','大于ma110','双向上','barRank','barRankPeriod','deaHL','deaTrend','deaPRank','deaGTS','deaGPRank','k','kTrend','k50','buy2','sell','sell2']])
        # print(df[['date','close','k','d']])
        print(df[['barHL_W','bTrend_W','po_W','bNo_W','date','close','增幅','大于ma110','双向上','barHL','bTrend','po','bNo','barRank','barRankPeriod','k','kTrend','k50','buy2','sell','sell2']])
        exit()
        # print(df[[0,'deaHL','deaTrend','barRankPeriod','bar','barHL','bTrend','po','bNo']])

    dfAppend.to_csv("/Users/miketam/Downloads/checkPolicy.csv", encoding="gbk", index=False)
    dfAppend.to_excel('/Users/miketam/Downloads/checkPolicy.xlsx', float_format='%.5f',index=False)

    # for i in resultArray:
    #     print(i)
    # print(dfAppend.dtypes)

