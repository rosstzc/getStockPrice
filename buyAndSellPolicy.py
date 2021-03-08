import baostock as bs
import pandas as pd
import openpyxl
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas_datareader as pdr

from func import *




#计算某天或某周都投资价值积分
def getScore(df, i, period):
    #加分、扣分、得分，分值描述

    #bar向上、位置是低位，加1分

    # df['加分'] = 0
    # df['扣分'] = 0
    # df['得分描述'] = ''
    # for i in range(len(df)):
    scoreAdd = 0
    scoreReduce = 0
    textAdd = ''
    textReduce = ''
    #bar方向+位置得分评估
    if i > 0:
        if df.at[i,'bar'] > 0:
            if df.at[i,'po'] == '低':
                scoreAdd += 1
                textAdd = 'bar向上低位+1'
            if df.at[i, 'po'] == '中':
                scoreAdd += 1
                textAdd = 'bar向上中位+1'
            if df.at[i, 'po'] == '高':
                scoreReduce += -1
                textReduce = 'bar向上高位-1'

        if df.at[i,'bar'] < 0:
            if df.at[i,'po'] == '低':
                scoreReduce += -1
                textReduce = 'bar向下低位-1'
            if df.at[i, 'po'] == '中':
                scoreReduce += -1
                textReduce = 'bar向下中位-1'
            if df.at[i, 'po'] == '高':
                scoreAdd += 1
                textAdd = 'bar向下高位+1'

        #kdj得分评估
        if df.at[i,'k'] < 20 and df.at[i,'k'] - df.at[i-1,'k'] > 0:
            scoreAdd += 1
            textAdd = textAdd + '，k向上少于20+1'

        if df.at[i, 'k'] > 20 and df.at[i - 1, 'k'] < 0:
            scoreAdd += 1
            textAdd = textAdd + '，k上穿过20+1'

        if df.at[i, 'k'] > 50 and df.at[i - 1, 'k'] < 50:
            scoreAdd += 1
            textAdd = textAdd + '，k上穿过50+1'

        if df.at[i,'k'] > 80 and df.at[i,'k'] - df.at[i-1,'k'] < 0:
            scoreAdd += -1
            textReduce = textReduce + '，k向下大于80-1'

        if df.at[i, 'k'] < 80 and df.at[i - 1, 'k'] > 80:
            scoreAdd += -1
            textReduce = textReduce + '，k下穿过80-1'


        if period == 'd':
            #股价大于ma100+1
            if  df.at[i,'大于ma110'] == '大于ma110':
                scoreAdd += 1
                textAdd = textAdd + '，大于ma110+1'


        #前两周bar降低，这周上升+1

        #bar值零线下上升+1
        if df.at[i,'bar'] > 0 and df.at[i,'dif'] < 0:
            scoreAdd += -1
            textReduce = textReduce + '，bar在0下上升+1'


        df.at[i,'加分'] = scoreAdd
        df.at[i,'减分'] = scoreReduce
        df.at[i,'加分描述'] = textAdd
        df.at[i,'减分描述'] = textReduce


    # df["加分"] = np.where((df['bar'] > 0) & (df['po'] == '低')| (df['po'] == '中'), (df['加分']+1) , df["加分"])  # 两均线比较
    # # df["加分"] = np.where((df['bar'] > 0) & (df['po'] == '') , (df['加分']+1) , df["加分"])  # 两均线比较
    # df["加分描述"] = np.where((df['bar'] > 0) , df['加分描述']+'', '')  # 两均线比较
    # # print(df.shape)

    return df

#取K线数据
def getKline(dfArray,stockName):
    dfAppend: DataFrame = pd.DataFrame() #
    #把所有df合并
    x = 0
    for df in dfArray:
        if len(stockName) > 1:
            # df['codeOnly'] = df['code']
            df['code'] = df['code'] +'.' +stockName[x]
        x = x + 1
        #画图test
        # path =  '/Users/miketam/Downloads/chartTest/day/'
        # getChartTest(df.copy(),path,'day')

        #从前往后画图，方便自己做看图

        #画图
        today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        path =  '/Users/miketam/Downloads/'+ today + '/chart/day/'
        getChart(df.copy(), path, 'tail', 150, 'day')

        # df = df[[ 'date','code','open','high','low','5low','5high','close', '增幅','volume', 'bar','bar021', 'bTrend', 'po', 'barKey', 'ema12Trend','ema26Trend','脉冲系统','force2','force12','barKeyCh','ema12','ema26','h/ema26%','c/ema26%','l/ema26%','upCFactor', 'upC','downC','h/Channel','c/Channel','l/Channel','lossStop','lossStop2', 'ema12Trend_W','ema26Trend_W']]
        df = df[[ 'date','date_W','code','open','high','low','5low','5high','close', '增幅','volume','diver','diverTest','diverUp', 'diverUpTest','bar','bar021','bar021_W2', 'bTrend', 'po', 'barKey', 'ema12Trend','ema21Trend','ema26Trend','脉冲系统','force2','force2Max','ema12','ema26','upCFactor', 'upC','downC','lossStop','lossStop2', 'ema12Trend_W','ema26Trend_W','ema21', 'ema21_W', 'ATR1','ATR2','ATR3','ATR-1','ATR-2','ATR-3','bar021_W22','bar120_W2']]
        df = df.iloc[::-1] #倒序，让最近排在前面

        dfAppend = dfAppend.append(df.head(200))
        # dfAppend = dfAppend.append(df)


    name = '日数据：股票最近K线数据'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend, name)


    # 从"平安银行"取交易日期列表
    dateArray = dfArray[0]['date'].values.tolist()
    dateArray.reverse()

    #策略：计算日线在0线下转向上的点，然后再人工找背离
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        condition = (df2['ema26Trend_W'] == 'up') | (df2['ema12Trend_W'] == 'up' )
        df3 = df2[(df2['bar021'] < 0) & condition ]
        dfAppend2 = dfAppend2.append(df3)
    name = '日数据：周趋势向上时，日bar值线0线下转向上的点，然后再人工找背离'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)

    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        condition = (df2['ema26Trend_W'] == 'down') & (df2['ema12Trend_W'] == 'down' )
        df3 = df2[(df2['bar021'] < 0) & condition]
        dfAppend2 = dfAppend2.append(df3)
    name = '日数据：周趋势向下时，日bar值0线下转向上的点，然后再人工找背离'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)


    #策略：在ema26向上趋势，找每天有比较合适买点的股票（是最近5天偏离最大）,再人工判断买点
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        condition = (df2['ema26Trend_W'] == 'up') | (df2['ema12Trend_W'] == 'up' )
        df3 = df2[(df2['5low'] > 0) & condition ]
        dfAppend2 = dfAppend2.append(df3)
    name = '日数据：周趋势向上时，日最低价偏离ema较大的点（最低价5天内偏离最大），然后人工找买点'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)
    # exit()
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        condition = (df2['ema26Trend_W'] == 'down') & (df2['ema12Trend_W'] == 'down' )
        df3 = df2[(df2['5low'] > 0) & condition ]
        dfAppend2 = dfAppend2.append(df3)
    name = '日数据：周趋势向下时，日最低价偏离ema较大的点（最低价5天内偏离最大），然后人工找买点'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)


    #突破ATR2
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2[df2['high'] >  df2['ATR2'] ]
        dfAppend2 = dfAppend2.append(df3)
    name = '日数据：今天最高价突破ATR2通道'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)

    #突破ATR-2
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2[df2['low'] <  df2['ATR-2'] ]
        dfAppend2 = dfAppend2.append(df3)
    name = '日数据：今天最低价突破ATR-2通道'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)

    #按日取周bar值从向下转向上（0下）
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2[df2['bar021_W2'] == 1]
        dfAppend2 = dfAppend2.append(df3)
    name = '日数据：按日取周bar值从向下转向上(0下)'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)

    # 按日取周bar值从向下转向上（0上）
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2[df2['bar021_W22'] == 1]
        dfAppend2 = dfAppend2.append(df3)
    name = '日数据：按日取周bar值从向下转向上（0上）'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)

    # 按日取周bar值从向上转向下
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2[df2['bar120_W2'] == 1]
        dfAppend2 = dfAppend2.append(df3)
    name = '日数据：按日取周bar值从向上转向下'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)

    # 日bar底部背离
    dfAppend2: DataFrame = pd.DataFrame()  # 重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2.loc[df2['diver'] != ' ']
        dfAppend2 = dfAppend2.append(df3)
    name = '日数据：日bar底部背离'
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    name = name + '-' + str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2, name)

    # 日bar底部背离
    dfAppend2: DataFrame = pd.DataFrame()  # 重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2.loc[df2['diverTest'] != ' ']
        dfAppend2 = dfAppend2.append(df3)
    name = '日数据：日bar准备底部背离'
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    name = name + '-' + str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2, name)


    # 日bar顶背离
    dfAppend2: DataFrame = pd.DataFrame()  # 重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        # df3 = df2.loc[df2['diverUp'].notnull()]
        df3 = df2.loc[df2['diverUp'] != ' ']
        dfAppend2 = dfAppend2.append(df3)
    name = '日数据：日bar顶部背离'
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    name = name + '-' + str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2, name)


    # 日bar准备顶背离
    dfAppend2: DataFrame = pd.DataFrame()  # 重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        # df3 = df2.loc[df2['diverUp'].notnull()]
        df3 = df2.loc[df2['diverUpTest'] != ' ']
        dfAppend2 = dfAppend2.append(df3)
    name = '日数据：日bar准备顶部背离'
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    name = name + '-' + str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2, name)

    return dfAppend




#在周线找股价偏离ema26比较大的股票, 1)但ema12向上，偏离排名。 2）当barKey为1，偏离排名。
def getWeekPriceDifEma26(dfArray, stockName):

    dfAppend: DataFrame = pd.DataFrame() #
    dfAppend2: DataFrame = pd.DataFrame() #
    #把所有df合并
    x = 0


    for df in dfArray:
        if len(stockName) > 1:
            df['code'] = df['code'] +'.' +stockName[x]
        x = x + 1

        df['ema100'] = pd.DataFrame.ewm(df['close'], span=100).mean()
        df['ema100Trend'] = np.where(df['ema100'] > df['ema100'].shift(1),'up','down')


        ##当ema12向上、ema100向上,这周股价下跌标记0，下一周：若ema12向上继续标记为0
        # df['增幅'] = df['增幅'].str.strip("%").astype(float) / 100
        condition1 = (df['ema12Trend'] == 'up') & (df['ema100Trend'] == 'up')
        condition2 = (df['增幅'] < 0) & (df['增幅'].shift(1) > 0)


        #画图
        today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        path =  '/Users/miketam/Downloads/'+ today +'/chart/week/'
        getChart(df.copy(), path, 'tail', 130, 'week')

        # df = df[['code', 'date','open','high','low', 'close', '5low','增幅', 'bar', 'bTrend', 'barKey','bar021','bNo', 'ema12Trend','ema26Trend','ema100Trend','脉冲系统','force2','force12','barKeyCh','ema12','ema26','ema100','upCFactor', 'upC','downC','c/ema26','h/Channel','c/Channel','l/Channel','lossStop','lossStop2']]
        df = df[['code', 'date','open','high','low', 'close', '5low','增幅', 'bar', 'diver','diverTest','diverUp','diverUpTest','bTrend', 'barKey','bar021', 'ema12Trend','ema26Trend','脉冲系统','force2','ema12','ema26','upCFactor', 'upC','downC','lossStop','lossStop2','ATR1','ATR2','ATR3','ATR-1','ATR-2','ATR-3']]
        df['key'] = np.where(condition1 & condition2, '0', '')
        dfAppend = dfAppend.append(df)


        # print(df)
        # outPutXlsx(df, '价格下跌2')
        # exit()

    # 从"平安银行"取交易日期列表
    dateArray = dfArray[0]['date'].values.tolist()
    dateArray.reverse()


    #策略：计算本周周线在0线下转向上的点，然后再人工找背离
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2[(df2['bar021'] < 0)]
        dfAppend2 = dfAppend2.append(df3)
    name = '周数据：计算周线0线下转向上的点，然后再人工找背离'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)


    #策略：在ema26向上趋势，找本周有比较合适买点的股票（是最近5天偏离最大）,再人工判断买点
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2[(df2['5low'] > 0) & (df2['ema26Trend'] == 'up')]
        dfAppend2 = dfAppend2.append(df3)
    name = '周数据：周线趋势向上时，股价偏离ema较大的点（最低价5周内偏离最大），然后人工找买点'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)

    # 突破ATR2
    dfAppend2: DataFrame = pd.DataFrame()  # 重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2[df2['high'] > df2['ATR2']]
        dfAppend2 = dfAppend2.append(df3)
    name = '周数据：这周最高价突破ATR2通道'
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    name = name + '-' + str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2, name)

    # 突破ATR-2
    dfAppend2: DataFrame = pd.DataFrame()  # 重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2[df2['low'] < df2['ATR-2']]
        dfAppend2 = dfAppend2.append(df3)
    name = '周数据：这周最低价突破ATR-2通道'
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    name = name + '-' + str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2, name)


    # 周bar底部背离
    dfAppend2: DataFrame = pd.DataFrame()  # 重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2.loc[df2['diver'] != ' ']
        dfAppend2 = dfAppend2.append(df3)
    name = '周数据：周bar底部背离'
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    name = name + '-' + str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2, name)

    # 周bar准备底部背离
    dfAppend2: DataFrame = pd.DataFrame()  # 重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2.loc[df2['diverTest'] != ' ']
        dfAppend2 = dfAppend2.append(df3)
    name = '周数据：周bar准备底部背离'
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    name = name + '-' + str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2, name)



    # 周bar顶背离
    dfAppend2: DataFrame = pd.DataFrame()  # 重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        # df3 = df2.loc[df2['diverUp'].notnull()]
        df3 = df2.loc[df2['diverUp'] != ' ']
        dfAppend2 = dfAppend2.append(df3)
    name = '周数据：周bar顶部背离'
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    name = name + '-' + str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2, name)

    # 周bar准备顶背离
    dfAppend2: DataFrame = pd.DataFrame()  # 重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        # df3 = df2.loc[df2['diverUp'].notnull()]
        df3 = df2.loc[df2['diverUp'] != ' ']
        dfAppend2 = dfAppend2.append(df3)
    name = '周数据：周bar准备顶部背离'
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    name = name + '-' + str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2, name)

    return


    #根据日期，把每周向上趋势（ema12向上），但出现下跌股票罗列出来
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        df3 = df2[df2['key'] == '0']
        dfAppend2 = dfAppend2.append(df3)
    name = '周数据：向上趋势出现下跌的周'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)
    # exit()

    # 根据日期，把每周所有股票的数据形成一个df，根据barKeyCh次数来排名
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        # 给df排序（barKeyCh高当排在前面）
        df2['barKeyCh'].fillna(0, inplace=True)
        df3 = df2.sort_values(by=['barKeyCh'], ascending=False)
        df3['排序'] = range(len(df3)) #增加一列序号，从0开始
        # 每个df只取每天20个数据
        # 把df组合为大dfAppend
        dfAppend2 = dfAppend2.append(df3.head(50))
    # 验证是否靠谱
    # print(dfAppend2)
    name = '周数据：0线下bar转变次数排序'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    # outPutXlsx(dfAppend2,name)

    #脉冲系统第一次出现做多

    #向下偏离最大的股票，寻找回调机会







        #当ema12向上、ema100向上,周股价处于下跌的股票，目标寻找哪些上升过程回调的股票（按下跌幅度排名）
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    for i in dateArray:
        # dfAppend['cTrend'] =  dfAppend['close'] / dfAppend['ema12'] - 1   #临时用一用
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        # df2['增幅'] = df2['增幅'].str.strip("%").astype(float) / 100
        condition1 = (df2['ema12Trend'] == 'up') &  (df2['ema100Trend'] == 'up')
        condition2 = df2['增幅'] < 0
        df3 = df2[condition1 & condition2]
        df4 = df3.sort_values(by=['增幅'], ascending=True) #按跌幅来排序
        df4['排序'] = range(len(df4)) #增加一列序号，从0开始
        dfAppend2 = dfAppend2.append(df4.head(50))
    print(dfAppend2)

    name = '周数据：当ema12向上、ema100向上,周股价处于下跌的股票'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)



    #当ema26向上，取价格偏离ema26正负10%, 或者通道值。
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    dfAppend['c/Channel2'] = abs(dfAppend['c/Channel'])  # 把偏离通道比如修改为正数，并且用新列承载
    dfAppend['c/ema26_2'] = abs(dfAppend['c/ema26'])  # 把偏离通道比如修改为正数，并且用新列承载
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        # condition1 = df2['ema26'] > df2['ema26'].shift(1)  这里是错的
        condition2 = abs(df2['c/ema26_2']) < 0.1
        df2 = df2[condition1 & condition2]
        df3 = df2.sort_values(by=['c/ema26_2'], ascending=False) #按照偏离程度来排序
        df3['排序'] = range(len(df3)) #增加一列序号，从0开始
        dfAppend2 = dfAppend2.append(df3.head(50))
    print(dfAppend2)

    name = '周数据：当ema26向上，取价格偏离ema26正负10%'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)
    # exit()


    #当ema12向上，根据股价偏离ema26来排序
    dfAppend2: DataFrame = pd.DataFrame() #重置df
    dfAppend['c/Channel2'] = abs(dfAppend['c/Channel'])  # 把偏离通道比如修改为正数，并且用新列承载
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        # df2 = df2[df2['ema12Trend'] == 'up']
        df3 = df2.sort_values(by=['c/Channel2'], ascending=False) #按照偏离程度来排序
        df3['排序'] = range(len(df3)) #增加一列序号，从0开始
        dfAppend2 = dfAppend2.append(df3.head(50))

    name = '周数据：ema12向上时的股价偏离通道排序'
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    name = name+ '-' +str(len(dfArray)) + '-' + today
    outPutXlsx(dfAppend2,name)


    #当barKey为1，根据股票偏离ema26来排序


    #当ema12向上，barKey为1，根据股价偏离ema26来排序


    return dfAppend2


 #当bar为负，找某周哪些假向上最多当股票，给他们排序，看看排前面转真向上的概率是不是大些
# def getBarChangeMaxStockWeekly(dfArray,stockName):
#
#     dfAppend: DataFrame = pd.DataFrame() #
#     dfAppend2: DataFrame = pd.DataFrame() #
#     #把所有df合并
#     x = 0
#     for df in dfArray:
#         if len(stockName) > 1:
#             df['code'] = df['code'] +'.' +stockName[x]
#         df['ema12Trend'] = np.where(df['ema12'] >df['ema12'].shift(1),'up','down' )
#         condition = (df['barKey'] == '1') | (df['barKey'] == '-1')
#         df['脉冲系统'] = np.where((df['ema12Trend'] == 'up') & condition,'买入','')
#         df = df[
#             ['code', 'date','high','low', 'close', '增幅', 'bar', 'bTrend', 'po', 'barKey', 'ema12Trend','脉冲系统','barKeyCh','ema26','upCFactor', 'upC','downC','lossStop','lossStop2','bTrend_W', 'po_W','barKey_W']]
#         df = df.drop([len(df) - 1])  # 把以前手工加的最后一行删除
#         dfAppend = dfAppend.append(df)
#         x = x + 1
#
#     # 从"平安银行"取交易日期列表
#     dfArray[0] = dfArray[0].drop([len(dfArray[0]) - 1])
#     dateArray = dfArray[0]['date'].values.tolist()
#
#     # 根据日期，把每周所有股票的数据形成一个df
#     for i in dateArray:
#         df2 = dfAppend[(dfAppend['date'] == i)].copy()
#         # 给df排序（barKeyCh高当排在前面）
#         df2['barKeyCh'].fillna(0, inplace=True)
#         df3 = df2.sort_values(by=['barKeyCh'], ascending=False)
#         df3['barKeyChRank'] = range(len(df3))
#         # 每个df只取每天20个数据
#         # 把df组合为大dfAppend
#         dfAppend2 = dfAppend2.append(df3.head(50))
#
#     # 验证是否靠谱
#     print(dfAppend2)
#     outPutXlsx(dfAppend2)
#     exit()
#     return


 #当bar为负，找某天哪些假向上最多当股票，给他们排序，看看排前面转真向上的概率是不是大些

#验证在止损价位置买入
def buyPolicyLossStop(dfArray,stockName):

    for df in dfArray:
        df['readyPrice'] = ''
        df['buy'] = ''
        df['sell'] = ''
        df['win'] = ''

        df['穿过止损'] = np.where(df['low'] < df['lossStop2'],'1','')
        closePriceArray = df['high'].values
        buyPrice = 0
        buyState = 0
        readyPrice = 0
        for i in range(len(df)):
            if i == 661:
                ddf= 11
            #计算止损点左边的阶段最高收盘价
            if df.at[i,'穿过止损'] == '1' and i > 3:
                for x in range(0,1000):
                    previous1 = closePriceArray[i-x-1]
                    previous2 = closePriceArray[i-x-2]
                    previous3 = closePriceArray[i-x-3]
                    if previous2 > previous1 and  previous2 > previous3: #找左边最近的阶段最高收盘价
                        readyPrice = previous2
                        df.at[i,'readyPrice'] = readyPrice
                        break
                    x = x + 1
                #如果之前有买入，那么今天就卖出
                if buyState == 1:
                    df.at[i,'sell'] = df.at[i,'lossStop2']
                    if df.at[i,'sell'] > buyPrice:
                        df.at[i,'win'] = '1'
                    else:
                        df.at[i, 'win'] = '0'
                    buyState = 0
                    buyPrice = 0


            #如果当天K线包含readyPrice，就买入
            if df.at[i,'high'] > readyPrice and readyPrice > df.at[i,'low'] and buyState == 0:
                buyPrice = readyPrice
                df.at[i,'buy'] = readyPrice
                buyState = 1


        df = df[
            ['code', 'date', 'high', 'low', 'close', '增幅', 'bar', 'bTrend', 'po', 'barKey',
             'barKeyCh', 'ema26', 'upCFactor', 'upC', 'downC', 'lossStop', 'lossStop2','穿过止损','readyPrice', 'buy','sell','win']]
        print(df)
        outPutXlsx(df)
        exit()



#验证周线脉冲系统买入
def buyPolicyWeekEma12up(dfArray,stockName):
    x = 0
    for df in dfArray:
        if len(stockName) > 1:
            df['code'] = df['code'] +'.' +stockName[x]
        df['ema12_WTrend'] = np.where(df['ema12_W'] >df['ema12_W'].shift(1),'up','down' )
        condition = (df['barKey_W'] == '1') | (df['barKey_W'] == '-1')
        df['脉冲系统_W'] = np.where((df['ema12_WTrend'] == 'up') & condition,'买入','')
        df = df[
            ['code', 'date','high','low', 'close', '增幅', 'bar', 'bTrend', 'po', 'barKey', 'ema12Trend','脉冲系统','barKeyCh','ema26','upCFactor', 'upC','downC','lossStop','lossStop2','bTrend_W', 'po_W','barKey_W']]
        df = df.drop([len(df) - 1])  # 把以前手工加的最后一行删除
    return



def getBarChangeMaxStock(dfArray,stockName):
    barChangeCountArray = []
    stockCodeArray = []

    dfAppend: DataFrame = pd.DataFrame() #
    dfAppend2: DataFrame = pd.DataFrame() #

    #把所有df合并
    x = 0
    for df in dfArray:
        #计算脉冲系统
        if len(stockName) > 1:
            df['code'] = df['code'] +'.' +stockName[x]
            # df['name'] = stockName[x]
        # df = getPulseSystem(df) #在计算日线、周线时已经添加此函数
        df = df[
            ['code', 'date','high','low', 'close', '增幅', 'bar', 'bTrend', 'po', 'barKey', 'ema12Trend','脉冲系统','barKeyCh','ema26','upCFactor', 'upC','downC','lossStop','lossStop2','bTrend_W', 'po_W','barKey_W']]
        df = df.drop([len(df) - 1])  # 把以前手工加的最后一行删除
        dfAppend = dfAppend.append(df)
        x = x + 1

        # print(dfAppend)
        # outPutXlsx(dfAppend)
        # exit()

    # 从"平安银行"取交易日期列表
    dfArray[0] = dfArray[0].drop([len(dfArray[0]) - 1])
    dateArray = dfArray[0]['date'].values.tolist()


    #根据日期，把每日所有股票的数据形成一个df
    for i in dateArray:
        df2 = dfAppend[(dfAppend['date'] == i)].copy()
        #给df排序（barKeyCh高当排在前面）
        df2['barKeyCh'].fillna(0, inplace=True)
        df3 = df2.sort_values(by=['barKeyCh'], ascending=False)
        df3['barKeyChRank'] = range(len(df3))
        #每个df只取每天20个数据
        #把df组合为大dfAppend
        dfAppend2 = dfAppend2.append(df3.head(50))

    #验证是否靠谱
    print(dfAppend2)
    outPutXlsx(dfAppend2)
    exit()
    return


#检查kdj的J值，J值在20一下向上或上穿20，开始监控，日线周线的情况
def buyPolicyKdjUp20(dfArray,StockName):
    dfAppend: DataFrame = pd.DataFrame() #
    x = -1
    for df in dfArray:
        x = x + 1
        df = df.drop([len(df) - 1])  # 把以前手工加的最后一行删除
        df['code'] = df['code'] +'.' +StockName[x]
        dfWeek = df.drop_duplicates(subset=['date_W'], keep='last', ignore_index=True)  # 只保留每周最后一条记录
        #找到J值在20以下或穿过20，并且周线处于高位，标记为"差"位置
        condition = (df['j20'] == 'j向上少于20') | (df['j20'] == 'j穿过20')
        df['poValue'] = np.where((df['po_W'] == '3') & (df['bTrend_W'] == '向上') & condition,'0','')
        df['pEma26'] = df['close']/df['ema26'] - 1
        # df['pEma26'] = df['pEma26'].apply(lambda x: format(x, '.2%'))

        df2 = df[['大于ma110','code', 'date','dw','close','pEma26','增幅','bar','bTrend','po','barKey','barKeyCh','j','j20','poValue','date_W', '增幅_W','bar_W','bTrend_W','po_W','barKey_W','j_W','j20_W']]

        if x == 0:
            print(list(df))
            print(df2)
            outPutXlsx(df2)
            exit()


        #找到最近一个星期10个交易日J值在20以下或穿过20
        df2 = df2.tail(1)
        df3 = df2[(df['j20'] == 'j向上少于20') | (df['j20'] == 'j穿过20')]



        #最后一天pEma26少于-3%，即股价少于ema26
        dftemp = df2.tail(1)
        pEma26 = dftemp['pEma26'].tolist()[0]

        #上周周bar值为上升
        dfWeek2 = dfWeek[-2:-1] #取倒数第二行
        barKey_W = dfWeek2['barKey_W'].tolist()[0]
        bTrend_W = dfWeek2['bTrend_W'].tolist()[0]
        po_W = dfWeek2['po_W'].tolist()[0]

        if df3.shape[0] > 0 :
        # if df3.shape[0] > 0 and bTrend_W == '向下' :
            dfAppend = dfAppend.append(df2)
            # dfAppend = dfAppend.append(df2,ignore_index=True)


        # print(df2)
        # outPutXlsx(df2)
        # exit()
    print(dfAppend)
    # outPutXlsx(dfAppend)

    exit()

    return

#根据周线bar柱的切换来判断买入，卖出。具体买入：1）向下中高位时，bar值从下降转上升，2）向上低位（已过金叉），做好技术止损； 卖出位置：向上中/高位bar值从升变降。 具体操作时间看日线
def buyPolicyBarChange(dfArray,StockName):
    for df in dfArray:

        dfWeek = df[['code', 'date_W', '增幅_W','bar_W','bTrend_W','po_W','barKey_W']]
        dfWeek = dfWeek.drop_duplicates(subset=['date_W'], keep='last')  # 只保留每周最后一条记录

        # 买入周
        condition1 = ((dfWeek['barKey_W'].shift(1) == '1') | (dfWeek['barKey_W'].shift(1) == '-1')  ) & ((dfWeek['barKey_W'].shift(2) == '-0') | (dfWeek['barKey_W'].shift(2) == '0')) #从0切换1
        condition2 = dfWeek['bTrend_W'] == ' ' #向下
        condition3 = (dfWeek['po_W'] == '高') | (dfWeek['po_W'] == '中')
        dfWeek['buy'] = np.where(condition1 & condition2 & condition3, 'buy', '') #向下中高位，0切换1的下一周标记为买入
        count = dfWeek[dfWeek['buy'] == 'buy'].shape[0]
        print('向下中高位0切换1的次数:' + str(count) )

        dfWeek['增幅_W2'] = dfWeek['增幅_W'].str.strip("%").astype(float) / 100 #把增幅百分数变小数
        count = dfWeek[ (dfWeek['增幅_W2']> 0) & (dfWeek['buy']  == 'buy')].shape[0]
        # print('向下中高位0切换1买入周，增幅是正数:' + str(count[0]) )
        print(dfWeek)
        exit()

        dfWeek['buy2'] = np.where( (dfWeek['bTrend_W'] == '向上') & condition1, 'buy', dfWeek['buy']) #向上低位
        dfWeek['buy2'] = np.where( (dfWeek['bTrend_W'] == '向上') & condition1, 'buy', dfWeek['buy']) #向上低位




        #卖出周
        condition4 = ((dfWeek['barKey_W'].shift(1) == '0') | (dfWeek['barKey_W'].shift(1) == '-0')  ) & ((dfWeek['barKey_W'].shift(2) == '-1') | (dfWeek['barKey_W'].shift(2) == '1')) #从1切换0
        dfWeek['sell'] = np.where(condition4 & (dfWeek['bTrend_W'] == '向上') & condition3, 'sell', '') #向上中高位

        # dfWeek = dfWeek[dfWeek['sell'] == 'sell' or ]



        temp = dfWeek[dfWeek['buy'] == 'buy'  ]
        print(temp)
        # dfWeek['follow2'] = np.where((dfWeek['barKey_W2'] == 1) & (dfWeek['barKey_W2'].shift(1) == 0),1,'')

        #总购买次数
        print('购买次数：' + str(temp.shape[0]))
        #购买当周股价是上涨到次数
        temp['增幅_W2'] = temp['增幅_W'].str.strip("%").astype(float) / 100
        temp2 = temp[temp['增幅_W2'] > 0]
        temp3 = temp[temp['增幅_W2'].shift(-1) > 0]
        print('购买当周上涨的次数：'+ str(temp2.shape[0]) + '，胜率：' + str(temp2.shape[0]/temp.shape[0]))

        #购买后第二周股价是上涨到次数
        print('购买后第二周涨的次数：'+ str(temp3.shape[0]) )

        exit()
    return




#根据macd Bar值趋势和长短周期的判断方法
def buyPolicyMacdBarKey(dfArray,StockName):


    #策略说明（回测）：
        #0) 先找到确定到值：第1，2周下降，第3周上升，在根据第3周的日bar值来评估第4周是否上升。 （自己根据这些历史数据进行分析）
        #1）预测bar值从下降趋势到转上升
        #2）先计算周线bar连续两次下降的两周，然后再统计第二周日线最后两天数据是否上升（比如这两根日期是5日，6日）或者一周内有2天上升，若是上升就把该股票纳入下周观察名单。（如果下周预测没有上升，但实际上升就把这周纳入观察名单）
            #注意：若此时周线处于向上高位，那么日线是否上升就意义不太。其他位置要注意观察日线连续上升，预示可能随时反转
        #3）再看看6日的小时线后两根，若是上升，下周一上升可能性大，标记为潜在买入点。 （若预测没升，但实际升了，又把当天纳入观察名单）
            #注意：
        #4）到了9日收盘（7日8日是周末），再看看9日是否上升，若是就在看看9日的后两根小时线，若是，明天为潜在买点。
        #5）重复以上操作，买点的开盘价买入

    for df in dfArray:
        df = df.drop([len(df)-1]) #把以前手工加的最后一行删除
        dfWeek = df[['date', '增幅_W', 'barKey', 'date_W', '增幅_W', 'barKey_W']]
        # print(dfWeek)
        # exit()
        dfWeek = dfWeek.drop_duplicates(subset=['date_W'], keep='last')  # 只保留每周最后一条记录
        # df2 = df[['date','close', '增幅', 'bar', 'barKey','加分','减分','加分描述', '减分描述','date_W', '增幅_W', 'bar_W', 'barKey_W','加分_W','减分_W','加分描述_W', '减分描述_W',]]
        # print(df2)
        # outPutXlsx(df2)
        # exit()



        dfWeek = df[['date','增幅','barKey','date_W','增幅_W','barKey_W']]
        # print(dfWeek)
        # exit()
        dfWeek = dfWeek.drop_duplicates(subset=['date_W'], keep='last')  #只保留每周最后一条记录
        # dfWeek = dfWeek.dropna(axis=0, how='any')
        dfWeek = dfWeek.dropna() #删除含有nan的行


        dfWeek['barKey_W2'] = dfWeek['barKey_W']
        dfWeek['barKey_W2'] =dfWeek['barKey_W2'].astype(int).abs() #读本地数据才要用，所以第一运行会报错
        dfWeek['follow'] = np.where((dfWeek['barKey_W2'] == 1) & (dfWeek['barKey_W2'].shift(1) == 0) & (dfWeek['barKey_W2'].shift(2) == 0),1,'') #第1，2周是0，第3是1
        dfWeek['follow2'] = np.where((dfWeek['barKey_W2'] == 1) & (dfWeek['barKey_W2'].shift(1) == 0),1,'')
                # df["加分描述"] = np.where((df['bar'] > 0) , df['加分描述']+'', '')  # 两均线比较

        df3= dfWeek.loc[(dfWeek['follow'] == '1')  ]
        # print(df3.shape[0])

        df2 = dfWeek.loc[(dfWeek['follow'] == '1') & (dfWeek['barKey_W2'].shift(-1) == 1) ] #第3周是1，第4周也是1
        df4 = dfWeek.loc[(dfWeek['follow'] == '1') & (dfWeek['barKey_W2'].shift(-1)  != 1) ] #第3周是1，第4周不是1
        # df2 = dfWeek.loc[dfWeek['follow'] == '1']
        print('第1，2周是0，第3周是1，第4周也是1: ' + str(df2.shape[0]))
        print(' #第1，2周是0，第3周是1，第4周不是1: ' + str(df4.shape[0]))

        # print(df2)
        # print(df4)
        # exit()
        #
        # df = getScore(df)
        # df2 = df[
        #     ['date', '增幅', 'bar', 'bTrend', 'po', 'barKey', 'date_W', '增幅_W', 'bar_W', 'bTrend_W', 'po_W', 'barKey_W',
        #      '加分', '减分', '加分描述', '减分描述']]
        # print(df2)
        # exit()

        df2 = df[['date','bTrend','po','barKey','date_W','增幅_W','bar_W','bTrend_W','po_W','barKey_W']]


    return


 # 买策略：用kdj、ma100、日macd趋势、周macd趋势来识别买点
def buyPolicyMacdKdj(dfArray,stockName):

    #逐个股票测试，然后把测试结果合并
    for df in dfArray:
        df = df.drop([len(df)-1]) #把以前手工加的最后一行删除

        #策略描述：
         # 1）周线位置：周线向上，低位或中位。
         # 2）日线Kdj的K向上，在50一下，接近50或穿过50； 在20一下

        print(df)
        # exit()
        dfnew = df

        dfnew['upC'] = dfnew['ema26'] * 1.04
        dfnew['downC'] = dfnew['ema26'] * 0.96

        # dfnew = df.loc[df['bTrend_W'] == '向上'] #周线向上
        # dfnew = dfnew.loc[(df['po_W'] == '低') | (df['po_W'] == '中')]  #周线在低、中位置

        # dfnew = dfnew.loc[((dfnew.bTrend == '向下') )]  #日线向上，日线向下并在高位

        # dfnew = dfnew.loc[((dfnew['bTrend'] == '向下') & (dfnew['po'] == '高'))]  #日线向上，日线向下并在高位

        dfnew = dfnew.loc[(dfnew['kTrend'] == 'k向上')  ]
        dfnew = dfnew.loc[(dfnew.k50 == 'k穿过50') ]
        # print(dfnew)
        # exit()
        # dfnew = dfnew.loc[(dfnew['jTrend'] == 'j向上')]
        # dfnew = dfnew.loc[(dfnew['j50'] == 'j穿过50') ]

        dfnew = dfnew.loc[(dfnew['大于ma110'] == '大于ma110') ]

        # dfnew = dfnew.loc[(dfnew.k50 == 'k少于50') | (dfnew.k50 == 'k穿过50') ]

        dfnew['buy'] = 0
        dfnew = pd.merge(df, dfnew,how='left')  #合并 （把处理过的值何合入原来df）

        #执行for循环到判断
        for i in range(len(dfnew)):
            if dfnew.at[i,'buy'] == 0:
                # 买入  #第二天开盘价或收盘价买入，都可以回测一下
                    #要加一个条件，如果涨停是买不入的！！！
                buyDayId = i+1
                if buyDayId == len(dfnew):
                    break
                priceBuy = dfnew.at[buyDayId,'close']
                dfnew.at[buyDayId, 'buy'] = 1
                dfnew.at[buyDayId,'priceBuy'] = priceBuy

                #止损价计算，取过去10天最低价
                indexStop =  dfnew.loc[i-10:buyDayId,'low'].idxmin() #最近10行k线最低价的索引
                priceStop = dfnew.loc[i-10:buyDayId,'low'].min() #最近10行k线最低价

                #卖出：买入后第二天开始计算，超过ema20的4%～6%的第二天收盘价卖出（这个价格不能低于买入价）
                for x in range(1,1000):
                    sellDayId = buyDayId+x
                    upC = dfnew.at[sellDayId,'upC']
                    low = dfnew.at[sellDayId,'low']
                    high = dfnew.at[sellDayId,'high']
                    #股价到达止损，即时卖出
                        #这里加个条件，如果当天跌停，是卖不出去的！！！！！！
                    if low < priceStop:
                        dfnew.at[buyDayId,'sellDay'] = dfnew.at[sellDayId,'date']
                        dfnew.at[buyDayId,'win'] = 0
                        sellPrice = priceStop
                        dfnew.at[buyDayId,'StopPriceDay'] = dfnew.at[indexStop,'date']
                        dfnew.at[buyDayId,'sellPrice'] = sellPrice
                        dfnew.at[buyDayId,'profit'] = sellPrice - priceBuy
                        dfnew.at[buyDayId,'profitP'] = sellPrice/priceBuy - 1
                        break
                    else:
                        if upC < high and dfnew.at[sellDayId+1,'close'] >  priceBuy: #超过通道后第二天收盘价卖出
                            dfnew.at[buyDayId, 'sellDay'] = dfnew.at[sellDayId + 1,'date']
                            dfnew.at[buyDayId, 'win'] = 1
                            sellPrice = dfnew.at[sellDayId + 1,'close']
                            dfnew.at[buyDayId, 'sellPrice'] = sellPrice
                            dfnew.at[buyDayId, 'profit'] = sellPrice - priceBuy
                            dfnew.at[buyDayId, 'profitP'] = sellPrice / priceBuy - 1
                            break
        # dfnew = dfnew.loc[(dfnew.buy == 0) | (dfnew.buy == 1)] #只显示触发购买相关的
        # print(dfnew.head())
        # print(df.columns.values.tolist())
        # exit()


        dfnew =  dfnew[[ 'code','bTrend_W', 'po_W', 'bNo_W', 'date', 'dw',  'close', '增幅', '大于ma110', '双向上', 'barHL',
                  'bTrend', 'po', 'bNo', 'barRank', 'barRankP', 'k', 'kTrend', 'k50','upC','buy','sellDay','sellPrice','win','profitP','StopPriceDay']]


        # 用一个单独函数来封装统计数据，方便日后调用和统计； 还有日后要通过循环参数（condition）变动跑策略，批量得到统计结果； 弄个测试用例，把各种情况做对比
        # 统计资金占用时间，计算所用总资金、总盈利，计算得到平均每次交易所需时间，资金，盈利，得到单位时间到盈利率。用1000股计算吧
        sta = getStatistic(dfnew,stockName)

        # print(dfnew.loc[dfnew.win==1]) #显示赚钱
        print(dfnew.loc[(dfnew.win==1) | (dfnew.win==0)]) #显示赚钱或亏钱

        # print(dfnew)
        # print(dfnew.loc[dfnew['buy']==1])
        # print('结果有多少行：',dfnew.shape[0])


        # print('ProfitPrecent：',dfnew.loc[dfnew.win==1,'profitP'].sum() + dfnew.loc[dfnew.win==0,'profitP'].sum())

        # dfnew.to_excel("/Users/miketam/Downloads/checkPolicy.xls", encoding="gbk", index=False)
        dfnew.to_excel('/Users/miketam/Downloads/checkPolicy.xlsx', float_format='%.5f',index=False)

        exit()
    return #返回回测结果


def getStatistic(dfSource, stockName):
    #用一个单独函数来封装统计数据，方便日后调用和统计； 还有日后要通过循环参数（condition）变动跑策略，批量得到统计结果； 弄个测试用例，把各种情况做对比

    shares = 1000
    #统计资金占用时间，计算所用总资金、总盈利，计算得到平均每次交易所需时间，资金，盈利，得到单位时间到盈利率。用1000股计算吧
    df = dfSource.loc[dfSource.buy==1]
        #用sellDay减去date可以得到持股时间段，然后把时间段累加得到总时间
    start = pd.to_datetime(df['sellDay'])
    end = pd.to_datetime(df['date'])
    tradeDays = dfSource.shape[0]/250 * 365
    tradeCount = df.shape[0] #交易次数（买+卖）
    dfTime = pd.DataFrame(start - end,columns=['hTime'])
    holdingTime = dfTime.sum().dt.days + tradeCount #累计持仓时间, 要在dfTime基础上，每次交易+1日才是每次持仓时间
    # holdingTime = dfTime.sum().dt.days #累计持仓时间
        #总资金、总盈利
    tradeWin = df.loc[df.win==1].shape[0]
    tradeWinPrecent = tradeWin/tradeCount
    funds = df['close'].sum() * shares #总资金（假设每次购买1000股）
    tax = funds * 0.0015 #每次买+卖到交易成本是0.0015
    proift = (df['close'] * df['profitP'] * shares).sum() - tax #扣除税费后到总利润
    avgFund = funds/tradeCount
    avgProfit = proift / tradeCount
    avgProfitPrecent =  avgProfit / avgFund #平均每次盈利百分比
    avgHoldingTime = int(holdingTime / tradeCount) + 1 #每次交易持仓时间
    profitPrecentYear = avgProfitPrecent * (365 / avgHoldingTime)

    # df.at[i, '最低价/买入'] = format(df.at[i, 'low'] / buyPrice - 1, '.2%')


    #形成文本
    stockName = '股票名：' + df.iat[0,0]
    tradeDays = '统计日数：' + str(int(tradeDays)) + '，持仓日数: ' + str(int(holdingTime))
    tradeCount = '交易次数：' + str(tradeCount)
    avgHoldingTime = '平均持仓时间：'  + str(avgHoldingTime)
    tradeWin = '盈利次数：' + str(tradeWin) + ', 胜率：' + str(tradeWinPrecent)
    funds = '总资金：' + str(int(funds))
    tax = '总税费：' + str(int(tax))
    proift = '扣税总收益：' + str(int(proift) )
    avgFund = '平均交易金额：'  + str(int(avgFund) )
    avgProfit = '平均交易利润(含亏损交易)：'  + str(int(avgProfit) )
    avgProfitPrecent = '平均每次交易利润率：'   + str(format(avgProfitPrecent,'.2%') )
    profitPrecentYear = '年化收益：'  + str(format(profitPrecentYear,'.2%') )

    print(
        stockName + '\n',
        tradeDays + '\n',
        tradeCount + '\n',
        tradeWin + '\n',
        tax + '\n',
        proift + '\n',
        avgFund + '\n',
        avgProfit + '\n',
        avgHoldingTime + '\n',
        avgProfitPrecent + '\n',
        profitPrecentYear + '\n',

    )
    # print(df)
    # print(avgHoldingTime)
    # exit()

    return



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
            # if barRank < 0.3 or barRankP < 0.3:
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
            barRankP = str2Float(df.at[i, 'barRankP'])
            key = 0
            if barRank < 0.3 or barRankP < 0.3:
                x = 0
                while df.at[i - x, 'deaHL'] != 'L':  # 当前卖出点向上找L点，如果barRank没有出现50%，就不卖
                    if str2Float(df.at[i - x, 'barRank']) > 0.5:
                        key = 1
                    x += 1
            if barRank < 0.3 and key == 1:
                df.at[i, 'sell'] = 'dea卖出'
            if barRankP < 0.3 and key == 1:
                df.at[i, 'sell2'] = 'dea卖出（短周期)'
    return df



def getMacdTrend(i,df,value,trend):
    # 识别当前点的DEA是向上或向下
    for x in range(1000):
        if i >= x:
            value2 = df.at[i - x, value] #基于当前i行，不断向前找H/L,找到就更新当前行

            # # # 处理bar值的周期排序（每个波动周期重新排序）
            # if value2 == 'H' or value2 == 'L':
            #     if x > 0:
            #         array = []
            #         value = getValueRank(i, df, 'bar', 'barRankP', array, x,'middle')
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
            df = getValueRank(i+x, df, 'bar', 'barRankP', array, m,'middle')[0]
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
            df = getValueRank(i+x, df, 'bar', 'barRankP', array, m,'middle')[0]
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