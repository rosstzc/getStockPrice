import baostock as bs
import pandas as pd
import openpyxl
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
from func import *

import time
import os
from buyAndSellPolicy import *


pd.set_option('display.width',210)
pd.set_option('display.max_columns',130)
pd.set_option('display.max_colwidth',130)
pd.set_option('display.max_rows', None)


def getHourData(kLineHourArray):
    dfAppend: DataFrame = pd.DataFrame() #
    for x in kLineHourArray:
        df: DataFrame = pd.DataFrame(x)
        df[2] = pd.to_numeric(df[2])  # 开盘价，把字符转化为数字
        df[3] = pd.to_numeric(df[3])  # 最高价，把字符转化为数字
        df[4] = pd.to_numeric(df[4])  # 最低价，把字符转化为数字
        df[5] = pd.to_numeric(df[5])  # 收盘价，把字符转化为数字
        # df["增幅"] = df[5]/df[5].shift() - 1
        # df["增幅"] = df["增幅"].apply(lambda x: format(x, '.2%'))
        # df['po'] = ''

        df = getDfMacd(df) #获取macd
        # df = getDfKdj(df)  #获取kdj

        # #计算dea的向上、向下趋势
        # index = len(df) #得到索引
        # barHLidList = df.loc[(df.barHL == 'H') | (df.barHL == 'L')].index.tolist() #bar所有HL点的的行的索引
        #
        # for i in range(index):  #这个循环效率，日后可以优化
        #     df = getDeaDifTrend(i, df, 'deaHL', 'deaTrend')  #计算bar值在本周期的百分比
        #
        #     # #估计bar值所在波形的位置
        #     df = getBarPositionDf(barHLidList,df,i)
        #     # print(df)
        #     # exit()
        #     df = getScore(df,i,'w')
        # #
        # # print(df[[0,'deaHL','deaTrend','barRankP','bar','barHL','bTrend','po','bNo']])
        # # exit()

        df.rename(columns={
            0: 'date',
            1: 'code',
            2: 'open',
            3: 'high',
            4: 'low',
            5: 'close',
        }, inplace=True)
        dfAppend = dfAppend.append(df)
    return dfAppend



#计算月线的各种数据
def getMonthData(kLineMonthArray):
    dfAppend: DataFrame = pd.DataFrame() #
    for x in kLineMonthArray:
        df: DataFrame = pd.DataFrame(x)
        df[2] = pd.to_numeric(df[2])  # 开盘价，把字符转化为数字
        df[3] = pd.to_numeric(df[3])  # 最高价，把字符转化为数字
        df[4] = pd.to_numeric(df[4])  # 最低价，把字符转化为数字
        df[5] = pd.to_numeric(df[5])  # 收盘价，把字符转化为数字
        df[6] = pd.to_numeric(df[6])  # 收盘价，把字符转化为数字

        df["增幅"] = df[5]/df[5].shift() - 1
        df['增幅'].fillna(0, inplace=True)


        # df["增幅"] = df["增幅"].apply(lambda x: format(x, '.2%'))
        df['po'] = ''

        df = getDfMacd(df) #获取macd
        df = getDfKdj(df)  #获取kdj


        df.rename(columns={
            0: 'date',
            1: 'code',
            2: 'open',
            3: 'high',
            4: 'low',
            5: 'close',
            6:'volume'
        }, inplace=True)


        #计算dea的向上、向下趋势
        index = len(df) #得到索引
        barHLidList = df.loc[(df.barHL == 'H') | (df.barHL == 'L')].index.tolist() #bar所有HL点的的行的索引

        barChangeCount = 0
        ema26DiffArray = np.array([])
        lowDiffArray = np.array([])
        lowDifEma26Array = np.array([])
        highDifEma26Array = np.array([])

        for i in range(index):  #这个循环效率，日后可以优化
            df = getDeaDifTrend(i, df, 'deaHL', 'deaTrend')  #计算bar值在本周期的百分比

            # #估计bar值所在波形的位置
            df = getBarPositionDf(barHLidList,df,i)
            # print(df)
            # exit()
            # df = getScore(df,i,'w')

            #当bar为负，计算在一周期内，又'-0'转'-1'的次数，方便后续全网做排序，选次数多的来买
            # temp = getBarChangeCount(df,i,barChangeCount)
            # df = temp[0]
            # barChangeCount = temp[1]


            # 计算通道（4个月95%线柱包含在通道内）
            temp = getEma26Channel(df, i, ema26DiffArray)
            df = temp[0]
            ema26DiffArray = temp[1]

            #计算止损价格（上升时，也可以用作止盈）
            temp = getLossStopPrice(df,i,lowDiffArray)
            df = temp[0]
            lowDiffArray = temp[1]

            ##判断当天是否为最近5天最合适买点（以ema26为基准）
            temp = getBuyPointBaseEma26(df, i, lowDifEma26Array)
            df = temp[0]
            lowDifEma26Array = temp[1]


            ##判断当天是否为最近5天最合适卖点（以ema26为基准）
            temp = getSellPointBaseEma26(df, i, highDifEma26Array)
            df = temp[0]
            highDifEma26Array = temp[1]

        # print(df[[0,'deaHL','deaTrend','barRankP','bar','barHL','bTrend','po','bNo']])
        # exit()

        df = getPulseSystem(df)
        dfAppend = dfAppend.append(df)

    return dfAppend



#计算周线都各种数据，比如macd,kdj
def getWeeklyData(kLineWeekArray):
    dfAppend: DataFrame = pd.DataFrame() #
    for x in kLineWeekArray:
        df: DataFrame = pd.DataFrame(x)
        df[2] = pd.to_numeric(df[2])  # 开盘价，把字符转化为数字
        df[3] = pd.to_numeric(df[3])  # 最高价，把字符转化为数字
        df[4] = pd.to_numeric(df[4])  # 最低价，把字符转化为数字
        df[5] = pd.to_numeric(df[5])  # 收盘价，把字符转化为数字
        df[6] = pd.to_numeric(df[6])  # 收盘价，把字符转化为数字

        df["增幅"] = df[5]/df[5].shift() - 1
        df['增幅'].fillna(0, inplace=True)


        # df["增幅"] = df["增幅"].apply(lambda x: format(x, '.2%'))
        df['po'] = ''

        df = getDfMacd(df) #获取macd
        df = getDfKdj(df)  #获取kdj


        df.rename(columns={
            0: 'date',
            1: 'code',
            2: 'open',
            3: 'high',
            4: 'low',
            5: 'close',
            6:'volume'
        }, inplace=True)


        #计算dea的向上、向下趋势
        index = len(df) #得到索引
        barHLidList = df.loc[(df.barHL == 'H') | (df.barHL == 'L')].index.tolist() #bar所有HL点的的行的索引

        barChangeCount = 0
        ema26DiffArray = np.array([])
        lowDiffArray = np.array([])
        lowDifEma26Array = np.array([])
        highDifEma26Array = np.array([])

        for i in range(index):  #这个循环效率，日后可以优化
            df = getDeaDifTrend(i, df, 'deaHL', 'deaTrend')  #计算bar值在本周期的百分比

            # #估计bar值所在波形的位置
            df = getBarPositionDf(barHLidList,df,i)
            # print(df)
            # exit()
            # df = getScore(df,i,'w')

            #当bar为负，计算在一周期内，又'-0'转'-1'的次数，方便后续全网做排序，选次数多的来买
            temp = getBarChangeCount(df,i,barChangeCount)
            df = temp[0]
            barChangeCount = temp[1]


            # 计算通道（4个月95%线柱包含在通道内）
            temp = getEma26Channel(df, i, ema26DiffArray)
            df = temp[0]
            ema26DiffArray = temp[1]

            #计算止损价格（上升时，也可以用作止盈）
            temp = getLossStopPrice(df,i,lowDiffArray)
            df = temp[0]
            lowDiffArray = temp[1]

            ##判断当天是否为最近5天最合适买点（以ema26为基准）
            temp = getBuyPointBaseEma26(df, i, lowDifEma26Array)
            df = temp[0]
            lowDifEma26Array = temp[1]


            ##判断当天是否为最近5天最合适卖点（以ema26为基准）
            temp = getSellPointBaseEma26(df, i, highDifEma26Array)
            df = temp[0]
            highDifEma26Array = temp[1]

        # print(df[[0,'deaHL','deaTrend','barRankP','bar','barHL','bTrend','po','bNo']])
        # exit()

        df = getPulseSystem(df) #脉冲系统
        df = getATRChannel(df)  # 生成ATR通道
        dfAppend = dfAppend.append(df)

    return dfAppend


#把日k线转为周K线
# def getWeekLyKlineDf(df):
#     # https://pandas-docs.github.io/pandas-docs-travis/timeseries.html#offset-aliases
#     # 周 W、月 M、季度 Q、10天 10D、2周 2W
#     period = 'W'
#     df.drop([len(df) - 1], inplace=True)
#     df['date'] = pd.to_datetime(df['date'])
#     df.set_index('date', inplace=True)
#     # df.index = pd.to_datetime(df.index, unit='s')
#     weekly_df = df.resample(p
#     weekly_df['open'] = df['open'].resample(period)
#     weekly_df['high'] = df['high'].resample(period, how='max')
#     weekly_df['low'] = df['low'].resample(period, how='min')
#     weekly_df['close'] = df['close'].resample(period, how='last')
#     # weekly_df['volume'] = df['volume'].resample(period, how='sum')
#     # weekly_df['amount'] = df['amount'].resample(period, how='sum')
#     # 去除空的数据（没有交易的周）
#     weekly_df = weekly_df[weekly_df.instrument.notnull()]
#     weekly_df.reset_index(inplace=True)
#     return weekly_df


#K线数据二次加工
def processKline(stockCodeArray, type, toFile = 1):
    Kline = getOnlyKline(stockCodeArray,toFile)
    kLineArray = Kline[0] #日k线
    dfAppend: DataFrame = pd.DataFrame()
    # 要获取的值：
    # 收盘数据：ma5，ma10，ma5动态，ma10动态，ma5是否大于ma10，是否双向上(含实时动态)，双向上最低价格，双向上价是否在高低范围内，ma10通道，收盘价相对ma5，ma10明天预测，ma10明天预测动态； 更多均线：20，30，60
    # macd:快线值、慢行值，快线动态，慢线动态
    # 实时数据：某个股价时，以上的数据再来一遍
    # 针对ema，上面数据再来一遍
    # 周线数据：周ma5...

    #计算周线的各种数据，最后合并为一个大df
    dfWeekAppend:DataFrame = pd.DataFrame()
    kLineWeekArray = Kline[1] #周k线
    dfWeekAppend= getWeeklyData(kLineWeekArray)
    if type == 'week':
        return [0,dfWeekAppend]

    # #计算月线各种数据
    # kLineMonthArray = Kline[2] #月k线
    # dfMonthAppend= getMonthData(kLineMonthArray)


    #计算小时线的数据
    # kLineHourArray = Kline[2] #小时k线
    # dfHourAppend= getHourData(kLineHourArray)


    #取出每个股票的k线数据，每个i代表1个股票的所有K线
    for x in kLineArray:
        kLineDf: DataFrame = pd.DataFrame(x)
        # kLineDf.columns = ["date", "code", "open", "high", "low", "close"]
        # 添加均线
        kLineDf[2] = pd.to_numeric(kLineDf[2])  # 开盘价，把字符转化为数字
        kLineDf[3] = pd.to_numeric(kLineDf[3])  # 最高价，把字符转化为数字
        kLineDf[4] = pd.to_numeric(kLineDf[4])  # 最低价，把字符转化为数字
        kLineDf[5] = pd.to_numeric(kLineDf[5])  # 收盘价，把字符转化为数字
        kLineDf[6] = pd.to_numeric(kLineDf[6])  # 收盘价，把字符转化为数字

        # 把时间列标准化时间格式
        kLineDf['dw'] = pd.to_datetime(kLineDf[0])
        # 输出这一天是周中的第几天，Monday=0, Sunday=6
        kLineDf['w'] = kLineDf['dw'].dt.isocalendar().week
        kLineDf['dw'] = kLineDf['dw'].dt.dayofweek + 1


        kLineDf["增幅"] = kLineDf[5]/kLineDf[5].shift() - 1
        kLineDf["增幅"] = kLineDf["增幅"].apply(lambda x: format(x, '.2%'))
        kLineDf["ma5"] = kLineDf[5].rolling(window=5).mean()  # 5日线
        kLineDf["ma10"] = kLineDf[5].rolling(window=10).mean()  # 10日线
        kLineDf["ma110"] = kLineDf[5].rolling(window=110).mean()  # 100

        kLineDf["Cma10"] = kLineDf[5]/kLineDf["ma10"] - 1
        kLineDf["Cma10"] = kLineDf["Cma10"].apply(lambda x: format(x, '.2%'))

        kLineDf["ma5VsMa10"] = np.where(kLineDf['ma5'] > kLineDf['ma10'] ,"大于","") #两均线比较

        #kLineDf["ma20"] = kLineDf[5].rolling(window=20).mean()  # 10日线

        #均线动态(收盘价)
        kLineDf["ma5Trend"] = np.where( kLineDf['ma5'] > kLineDf['ma5'].shift(+1) ,"向上","")
        kLineDf["ma10Trend"] = np.where( kLineDf['ma10'] > kLineDf['ma10'].shift(+1) ,"向上","")

        #5日线，10日线是否双向上
        kLineDf["ma5ma10Trend"] = np.where((kLineDf["ma5Trend"]=="向上") & (kLineDf["ma10Trend"]=="向上"),"是","")

        #收盘价是否大于ma110
        kLineDf["大于ma110"] = np.where( kLineDf[5] > kLineDf['ma110'],"大于ma110","")


        new = ['用双向上基线做的预测值']  #新增一行，方便显示均线向上的最低值。一定要价true这个参数
        kLineDf = kLineDf.append(new,ignore_index=True)

        # 计算最低向上价格。把df列变为数组，在数组运算后再变为df
        closePriceArray = kLineDf[5].values
        ma5Array = kLineDf["ma5"].values
        ma10Array = kLineDf["ma10"].values
        kLineDf["priceForMa5Up"] = getPriceForMaUp(5,closePriceArray,ma5Array)
        kLineDf["priceForMa10Up"] = getPriceForMaUp(10,closePriceArray,ma10Array)
        kLineDf["priceForMa5Ma10Up"] = np.where(kLineDf["priceForMa5Up"] > kLineDf["priceForMa10Up"],kLineDf["priceForMa5Up"],kLineDf["priceForMa10Up"])#双向上最低价
        kLineDf["growthForpriceForMa5Ma10Up"] = kLineDf["priceForMa5Ma10Up"]/ kLineDf[5].shift() - 1
        kLineDf["growthForpriceForMa5Ma10Up"] = kLineDf["growthForpriceForMa5Ma10Up"].apply(lambda x: format(x, '.2%'))


        # #给双向上指标增加动态
        kLineDf["ma5ma10Trend"] = np.where((kLineDf["ma5ma10Trend"] == '是')&(kLineDf[4] < kLineDf["priceForMa5Ma10Up"]),'是，有向下', kLineDf["ma5ma10Trend"])
        kLineDf["ma5ma10Trend"] = np.where((kLineDf["ma5ma10Trend"] == '')&(kLineDf[3] > kLineDf["priceForMa5Ma10Up"]),'有双向上', kLineDf["ma5ma10Trend"])

        # #双向上价是否在K线内
        # kLineDf["priceForMa5Ma10UpInKLine"] = np.where((kLineDf[4] < kLineDf["priceForMa5Ma10Up"])&(kLineDf["priceForMa5Ma10Up"] < kLineDf[3]),'Y','')

        #把双向上基线放放到收盘价作为参考，并更新ma5、ma10作为参考
        index = len(kLineDf)-1
        # kLineDf.at[index,5] = kLineDf.at[index, 'priceForMa5Ma10Up']  #屏蔽这个预测收盘价
        kLineDf["ma5"] = kLineDf[5].rolling(window=5).mean() #再次更新一下均线
        kLineDf["ma10"] = kLineDf[5].rolling(window=10).mean()  #再次更新一下均线
        kLineDf.at[index, 1] = x[0][1]

        #双向上基线对比10日线
        kLineDf["priceForMa5Ma10UpVsMa10"] = kLineDf["priceForMa5Ma10Up"] / kLineDf["ma10"] - 1
        kLineDf["priceForMa5Ma10UpVsMa10"] = kLineDf["priceForMa5Ma10UpVsMa10"].apply(lambda x: format(x, '.2%'))

        # ##双向上价/收盘价
        # kLineDf["priceForMa5Ma10UpVsClosePrice"] = kLineDf["priceForMa5Ma10Up"] / kLineDf[5] - 1
        # kLineDf["priceForMa5Ma10UpVsClosePrice"] = kLineDf["priceForMa5Ma10UpVsClosePrice"].apply(lambda x: format(x, '.2%'))
        #
        # # kLineDf["priceForMa5Ma10UpVsLowPrice"] #最低价/双向上价
        # kLineDf["lowPriceVsPriceForMa5Ma10Up"] = kLineDf[4] / kLineDf["priceForMa5Ma10Up"] - 1
        # kLineDf["lowPriceVsPriceForMa5Ma10Up"] = kLineDf["lowPriceVsPriceForMa5Ma10Up"].apply(lambda x: format(x, '.2%'))
        #
        # # kLineDf["priceForMa5Ma10UpVsHighPrice"] #最高价/双向上价
        # kLineDf["highPriceVsPriceForMa5Ma10Up"] = kLineDf[3]/ kLineDf["priceForMa5Ma10Up"] - 1
        # kLineDf["highPriceVsPriceForMa5Ma10Up"] = kLineDf["highPriceVsPriceForMa5Ma10Up"].apply(lambda x: format(x, '.2%'))

        #计算kdj
        kLineDf = getDfKdj(kLineDf)

        # # #MACD相关
        kLineDf = getDfMacd(kLineDf)
        # 去掉倒数第二行的bar021数据，因为这行是由于之前新增行数据造成
        kLineDf.at[len(kLineDf) - 2, 'bar021'] = np.nan

        #判断dif、dea波浪线高低点
        # kLineDf['difHL'] =  np.where((kLineDf['dif'] - kLineDf['dif'].shift(1) >= 0 )&(kLineDf['dif'] - kLineDf['dif'].shift(-1) >= 0 ),'H',kLineDf['dif'])
        # kLineDf['difHL'] =  np.where((kLineDf['dif'] - kLineDf['dif'].shift(1) <= 0 )&(kLineDf['dif'] - kLineDf['dif'].shift(-1) <= 0 ),'L',kLineDf['difHL'])
        kLineDf['deaHL'] =  np.where((kLineDf['dea'] - kLineDf['dea'].shift(1) >= 0 )&(kLineDf['dea'] - kLineDf['dea'].shift(-1) >= 0 ),'H',kLineDf['dea'])
        kLineDf['deaHL'] =  np.where((kLineDf['dea'] - kLineDf['dea'].shift(1) <= 0 )&(kLineDf['dea'] - kLineDf['dea'].shift(-1) <= 0 ),'L',kLineDf['deaHL'])

        # # 计算bar的HL点
        # kLineDf['barHL'] = np.where((kLineDf['bar'].shift(1) > 0) & (kLineDf['bar'] < 0), 'H', '')
        # kLineDf['barHL'] = np.where((kLineDf['bar'].shift(1) < 0) & (kLineDf['bar'] > 0), 'L', kLineDf['barHL'])
        # kLineDf['bTrend'] = np.where((kLineDf['bar'] > 0),'向上','向下')
        #


        #计算dea/price
        kLineDf['deaP'] = kLineDf['dea'] / kLineDf[5] * 100


        #计算增量（今天减昨天）、增量/股价比，然后转化为百分数
        kLineDf['difGrowth'] = (kLineDf['dif'] - kLineDf['dif'].shift(1))
        kLineDf['difGP'] = kLineDf['difGrowth'] / kLineDf[5] * 100
        kLineDf['deaGrowth'] = kLineDf['dea'] - kLineDf['dea'].shift(1)
        kLineDf['deaGP'] = kLineDf['deaGrowth'] / kLineDf[5] * 100

        # kLineDf['difGrowth'] =kLineDf['difGrowth'].apply(lambda x: format(x, '.2%'))
        # kLineDf['difGP'] = kLineDf['difGP'].apply(lambda x: format(x, '.2%'))
        # kLineDf['deaGrowth'] =  kLineDf['deaGrowth'].apply(lambda x: format(x, '.2%'))
        # kLineDf['deaGP'] =  kLineDf['deaGP'].apply(lambda x: format(x, '.2%'))


        # print(kLineDf[['dif','difHL','deaGrowth','difGP','dea','deaHL','deaGrowth' ,'deaGP']])
        # exit()
        ##制作图macd
        # plt.plot(df.ds, dif, label='dif',color='orange')
        # plt.plot(df.ds, deaa, label='dea', )
        # # plt.plot(df.ds, macd, label='macd', color='Magenta')
        # plt.legend(loc='upper left')
        # plt.show()

# ########下面开始计算ema的数据##########
#         kLineDf['closeEma'] = kLineDf[5]  #为方便ema双向上的预测收盘价，新增一列收盘价
#
#         kLineDf['ema12'] = exp1
#         kLineDf['ema26'] = exp2
#
#         kLineDf["ema12VsEma26"] = np.where(kLineDf['ema12'] > kLineDf['ema26'] ,"大于","") #两均线比较
#
#         #均线动态(收盘价)
#         kLineDf["ema12Trend"] = np.where( kLineDf['ema12'] > kLineDf['ema12'].shift(+1) ,"向上","")
#
#         kLineDf["ema26Trend"] = np.where( kLineDf['ema26'] > kLineDf['ema26'].shift(+1) ,"向上","")
#
#         #5日线，10日线是否双向上
#         kLineDf["ema12ema26Trend"] = np.where((kLineDf["ema12Trend"]=="向上") & (kLineDf["ema26Trend"]=="向上"),"是","")
#
#         #计算ema线向上的最低价格
#         kLineDf["priceForEma12Up"] = getPriceForEmaUp(12,kLineDf['ema12'].shift(+1)) #当前行计算是下一日的最低向上价格
#         kLineDf["priceForEma26Up"] = getPriceForEmaUp(26,kLineDf['ema26'].shift(+1))
#         kLineDf["priceForEma12Ema26Up"] = np.where(kLineDf["priceForEma12Up"] > kLineDf["priceForEma26Up"],kLineDf["priceForEma12Up"],kLineDf["priceForEma26Up"])
#
#         #更新最后一个收盘价(EMA)作为预测，然后在更新ema均线，同时也更新两个ema线
#         kLineDf.at[index,'closeEma'] = kLineDf.at[index, 'priceForEma12Ema26Up']
#         kLineDf['ema12'] = kLineDf['closeEma'].ewm(span=12, adjust=False).mean()
#         kLineDf['ema26'] = kLineDf['closeEma'].ewm(span=26, adjust=False).mean()
#
#         # #给ema双向上指标增加动态
#         kLineDf["ema12ema26Trend"] = np.where((kLineDf["ema12ema26Trend"] == '是')&(kLineDf[4] < kLineDf["priceForEma12Ema26Up"]),'是，有向下', kLineDf["ema12ema26Trend"])
#         kLineDf["ema12ema26Trend"] = np.where((kLineDf["ema12ema26Trend"] == '')&(kLineDf[3] > kLineDf["priceForEma12Ema26Up"]),'有双向上', kLineDf["ema12ema26Trend"])
#
#         #双向上价是否在K线内
#         kLineDf["priceForEma12Ema26UpInKLine"] = np.where((kLineDf[4] < kLineDf["priceForEma12Ema26Up"])&(kLineDf["priceForEma12Ema26Up"] < kLineDf[3]),'Y','')
#
#         # ema双向上基线对比ema26日线
#         kLineDf["priceForEma12Ema26UpVsEma26"] = kLineDf["priceForEma12Ema26Up"] / kLineDf["ema26"] - 1
#         kLineDf["priceForEma12Ema26UpVsEma26"] = kLineDf["priceForEma12Ema26UpVsEma26"].apply(lambda x: format(x, '.2%'))
#
#         ##ema双向上价/收盘价
#         kLineDf["priceForEma12Ema26UpVsClosePrice"] = kLineDf["priceForEma12Ema26Up"] / kLineDf[5] - 1
#         kLineDf["priceForEma12Ema26UpVsClosePrice"] = kLineDf["priceForEma12Ema26UpVsClosePrice"].apply(lambda x: format(x, '.2%'))
#
#          #最低价/ema双向上价
#         kLineDf["lowPriceVspriceForEma12Ema26Up"] = kLineDf[4] / kLineDf["priceForEma12Ema26Up"] - 1
#         kLineDf["lowPriceVspriceForEma12Ema26Up"] = kLineDf["lowPriceVspriceForEma12Ema26Up"].apply(lambda x: format(x, '.2%'))
#
#          #最高价/ema双向上价
#         kLineDf["highPriceVspriceForEma12Ema26Up"] = kLineDf[3] / kLineDf["priceForEma12Ema26Up"] - 1
#         kLineDf["highPriceVspriceForEma12Ema26Up"] = kLineDf["highPriceVspriceForEma12Ema26Up"].apply(lambda x: format(x, '.2%'))


        # #实时价格
        # kLineDf["ma10RT"]  #在某股价时10均线值
        # kLineDf["ma10TrendRT"]  #在某股价时10均线动态

        # #EMA实时
        # kLineDf["ema22RT"]  #在某股价时10均线值
        # kLineDf["ema22TrendRT"]  #在某股价时10均线动态
        #

        kLineDf.rename(columns={
            0: 'date',
            1: 'code',
            2: 'open',
            3: 'high',
            4: 'low',
            5: 'close',
            6: 'volume',

            # 'ma5': 'ma555',
            # 'ma10': 'ma555',
            # 'ma5VsMa10': 'ma555',
            'ma5Trend': 'ma5动态',
            'ma10Trend': 'ma10动态',
            'priceForMa5Up': 'ma5向上价',
            'priceForMa10Up': 'ma10向上价',
            'priceForMa5Ma10Up': 'ma双向上价',
            'growthForpriceForMa5Ma10Up': '双向上最低升幅',
            'ma5ma10Trend': '双向上',
            'priceForMa5Ma10UpInKLine': 'ma双向上价K线内',
            'priceForMa5Ma10UpVsMa10': 'ma双向上价/10日线',
            'priceForMa5Ma10UpVsClosePrice': 'ma双向上价/收盘价',
            'lowPriceVsPriceForMa5Ma10Up': '最低价/ma双向上价',
            'highPriceVsPriceForMa5Ma10Up': '最高价/ma双向上价',

            # 'ema12': 'T20',
            # 'ema26': 'T20',
            'closeEma':'收盘价EMA用',
            'ema12Trend': 'ema12动态',
            'ema26Trend': 'ema26动态',
            'ema12ema26Trend': 'ema双向上',
            'priceForEma12Up': 'ema12向上价',
            'priceForEma26Up': 'ema26向上价',
            'priceForEma12Ema26Up': 'ema双向上价',
            'priceForEma12Ema26UpInKLine': 'ema双向上价K线内',
            'priceForEma12Ema26UpVsEma26': 'ema双向上价/ema26',
            'priceForEma12Ema26UpVsClosePrice': 'ema双向上价/收盘价',
            'lowPriceVspriceForEma12Ema26Up': '最低价/ema双向上价',
            'highPriceVspriceForEma12Ema26Up': '最高价/ema双向上价',
        }, inplace=True)

        dfAppend = dfAppend.append(kLineDf) #带上自己的索引
        # dfAppend = dfAppend.append(kLineDf,ignore_index=True)

        ### 结果集输出到csv文件 ####
    # if toFile == 1:
        # dfAppend.to_csv("/Users/miketam/Downloads/processKline.csv", encoding="gbk")
        # dfAppend.to_csv("/Users/miketam/Downloads/processKline.csv", encoding="gbk", index=False)
        # macd.to_csv("/Users/miketam/Downloads/processKline_macd.csv", encoding="gbk", index=False)
        # print(dfAppend)
        # dfAppend.to_excel('/Users/miketam/Downloads/processKline.xlsx', float_format='%.5f',index=False)
    # return [dfAppend,dfWeekAppend,dfHourAppend]
    return [dfAppend,dfWeekAppend]

def getHourKline(stockCodeArray, start_date, end_date):
    klineHourArray = []
    for i in stockCodeArray:
        data_list = []
        code = codeFormat(i)
        rs = bs.query_history_k_data_plus(code,
                                          # 0    1     2    3   4    5      6       7      8        9      10     11          12    13    14    15      16     17
                                          # "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                                          "date,code,open,high,low,close",
                                          start_date=start_date, end_date=end_date,
                                          frequency="60", adjustflag="2")
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        # 去掉停牌的日期的数据
        temp_list = []
        for i in range(len(data_list)):
            if data_list[i][5] != data_list[i - 1][5] or data_list[i][3] != data_list[i - 1][3] and i > 0:
                temp_list.append(data_list[i])
        data_list = temp_list
        # df: DataFrame = pd.DataFrame(data_list)
        # print(df)
        # exit()
        klineHourArray.append(data_list)
    return klineHourArray


#获取月K线
def getMonthKline(stockCodeArray, start_date, end_date):
    klineMonthArray = []
    for i in stockCodeArray:
        data_list = []
        code = codeFormat(i)
        rs = bs.query_history_k_data_plus(code,
                                          # 0    1     2    3   4    5      6       7      8        9      10     11          12    13    14    15      16     17
                                          # "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                                          "date,code,open,high,low,close,volume",
                                          start_date= start_date, end_date= end_date,
                                          frequency="m", adjustflag="2")
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())

        #去掉停牌的日期的数据
        temp_list = []
        for i in range(len(data_list)):
            if data_list[i][5] != data_list[i-1][5] or data_list[i][3] != data_list[i-1][3] and i > 0:
                temp_list.append(data_list[i])
        data_list = temp_list
        # df: DataFrame = pd.DataFrame(data_list)
        # print(df)
        # exit()
        klineMonthArray.append(data_list)
    return klineMonthArray



#获取周K线
def getWeeklyKline(stockCodeArray, start_date, end_date):
    klineWeekArray = []
    for i in stockCodeArray:
        data_list = []
        code = codeFormat(i)
        rs = bs.query_history_k_data_plus(code,
                                          # 0    1     2    3   4    5      6       7      8        9      10     11          12    13    14    15      16     17
                                          # "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                                          "date,code,open,high,low,close,volume",
                                          start_date= start_date, end_date= end_date,
                                          frequency="w", adjustflag="2")
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())

        #去掉停牌的日期的数据
        temp_list = []
        for i in range(len(data_list)):
            if data_list[i][5] != data_list[i-1][5] or data_list[i][3] != data_list[i-1][3] and i > 0:
                temp_list.append(data_list[i])
        data_list = temp_list
        # df: DataFrame = pd.DataFrame(data_list)
        # print(df)
        # exit()

        klineWeekArray.append(data_list)
    return klineWeekArray


#获取最基础到K线数据
def getOnlyKline(stockCodeArray,toFile=1,start_date='2018-01-06',end_date='2023-10-31'):
    #如果toFile=0就直接读取本地csv文件
    if toFile == 0:
        df = pd.read_csv('/Users/miketam/Downloads/getOnlyKline_300.csv',sep=',')
        # df = pd.read_csv('/Users/miketam/Downloads/getOnlyKline.csv', header=None, sep=',')
        # 得先把数据按股票拆分为一个个array，每个股票的k线是一个array
        dfArray = dfDivide(stockCodeArray,df)
        kLineArray = []
        for i in dfArray:
            j = i.values
            kLineArray.append(j)
        return kLineArray

    arrayMerage = []
    klineArray = []



    for i in stockCodeArray:
        data_list = []
        code = codeFormat(i)
        rs = bs.query_history_k_data_plus(code,
                                          # 0    1     2    3   4    5      6       7      8        9      10     11          12    13    14    15      16     17
                                          # "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                                          "date,code,open,high,low,close,volume",
                                          start_date= start_date, end_date= end_date,
                                          frequency="d", adjustflag="2")
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())

        #去掉停牌的日期的数据
        temp_list = []
        for i in range(len(data_list)):
            if data_list[i][5] != data_list[i-1][5] or data_list[i][3] != data_list[i-1][3] and i > 0:
                temp_list.append(data_list[i])
        data_list = temp_list

        arrayMerage.extend(data_list)
        klineArray.append(data_list) #用在二次处理
    result: DataFrame = pd.DataFrame(arrayMerage)
    result.columns =  ["date","code","open","high","low","close","volume"]

    # 获取周K线数据
    # klineMonthArray = getMonthKline(stockCodeArray, start_date, end_date)
    klineWeekArray = getWeeklyKline(stockCodeArray, start_date, end_date)
    # KlineHourArray = getHourKline(stockCodeArray, start_date, end_date)

    # 用日线数据给周线数据补充最后一周数据
    for x in range(len(klineWeekArray)):
        week = klineWeekArray[x]  #一个股票的周k线
        week.reverse()
        day = klineArray[x]  #一个股票的日k线
        day.reverse() #倒序，最后一天在前面
        dateDayLast = day[0][0]
        dateWeekLast = week[0][0]
        temp = []
        #通过日数据计算最后一周数据
        weekDate = getYearWeekFromDate(dateDayLast) #计算是本年的第几个周
        closeLastWeek = day[0][5] #这周最后一天收盘价就是周收盘价
        openLastWeek = day[0][2]
        highLastWeek = day[0][3]
        lowLastWeek = day[0][4]
        for d in day:
            if getYearWeekFromDate(d[0]) == weekDate:# 从后向前查询这周每天数据
                openLastWeek = d[2] #这个周的第一天开盘价就是周开盘价
                if d[3] > highLastWeek: #取最大值
                    highLastWeek = d[3]
                if d[4] < lowLastWeek:
                    lowLastWeek = d[4]
            else:
                break
        weekLast = [day[0][0], day[0][1], openLastWeek, highLastWeek, lowLastWeek, closeLastWeek ]
        if dateDayLast == dateWeekLast:  #若果最后一日和最后一周是在相同周，就覆盖，否则就新建
            week[0] = weekLast
        else:
            week.insert(0,weekLast)
        week.reverse()
        day.reverse()



    if toFile == 1:
        result.to_excel('/Users/miketam/Downloads/getOnlyKline.xlsx', float_format='%.5f', index=False)
        result.to_csv("/Users/miketam/Downloads/getOnlyKline.csv", encoding="gbk", index=False)
        # print(result)
    return [klineArray, klineWeekArray]
    # return [klineArray, KlineWeekArray, KlineHourArray]




#获取均线动态
def getMaLineTrend(stockCodeArray,stockNameArray):
    array = []
    temp = ''
    maMultiStockPd = ''
    x = 0
    for i in stockCodeArray:
        stockName = stockNameArray[x]
        x = x + 1
        data_list = []
        code = codeFormat(i)
        rs = bs.query_history_k_data_plus(code,
                                          # 0    1     2    3   4    5      6       7      8        9      10     11          12    13    14    15      16     17
                                          # "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                                          "date,code,open,high,low,close",
                                          start_date='2020-01-01', end_date='2021-12-31',
                                          frequency="d", adjustflag="2")
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())

        result = pd.DataFrame(data_list)
        #添加均线
        result[6] = result[5].rolling(window=5).mean()  # 5日线
        result[7] = result[5].rolling(window=10).mean()  # 10日线
        #result[8] = result[5].rolling(window=20).mean()  # 10日线
        #result.columns = ["date","code","open","high","low","close","ma5","ma10","ma20"]

        #判断均线向上向下
        array = result.values #转为数组
        ma5 = ""
        ma10 = ""
        maArrayOneStock = []
        # maArray = []
        m = 0  # 双向下个数
        n = 0  # ma5向上
        for j in range(0, len(array)): #获取上一个，下一个
            Current = array[j]
            Prev = array[j - 1]
            if Current[6] > 0 and Prev[6] > 0:
                if Current[6] > Prev[6]:
                    ma5 = "向上_5"
                else:
                    ma5 = ""
            if Current[7] > 0 and Prev[7] > 0:
                if Current[7] > Prev[7]:
                    ma10 = "向上_10"
                else:
                    ma10 = ""


            # 这里预留位置，调用函数取"双均线连续3天向下，5日线今天向上"
            # 在近4天，有1个或2个"5日向上"，其余为双向下
            if j >= (len(array) - 4):
                if ma5 == '' and ma10 == '':
                    m = m + 1
                if ma5 == '向上_5' and ma10 == '':
                    n = n + 1
            if j == (len(array) - 1):
                if (n == 1 and m == 3) or (n == 2 and m == 2):
                    ma5 = ma5 + '快来看我'

            maArrayOneDay = [Current[0], ma5, ma10]  #后续日期做索引，df merge时不重复
            maArrayOneStock.append(maArrayOneDay)



        temp = pd.DataFrame(maArrayOneStock)
        temp.columns = ["date", stockName + "_ma5",str(i) + "_ma10"]
        # temp.set_index('date',inplace=True, drop=True)
        if x == 1:
            maMultiStockPd = temp
        else:
            maMultiStockPd = pd.merge(maMultiStockPd,temp,on='date')
    ### 结果集输出到csv文件 ####
    print(maMultiStockPd)
    # maMultiStockPd.to_csv("/Users/miketam/Downloads/getMaline.csv", encoding="gbk", index=False)
    maMultiStockPd.to_excel('/Users/miketam/Downloads/getMaline.xlsx', float_format='%.5f', index=False)
    return


