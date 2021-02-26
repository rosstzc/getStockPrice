import baostock as bs
import pandas as pd
import openpyxl
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
from func import *
from buyAndSellPolicy import *
from doubleKlineMethod import *
# from chart import *
import time



pd.set_option('display.width',250)
pd.set_option('display.max_columns',130)
pd.set_option('display.max_colwidth',130)
pd.set_option('display.max_rows', None)




#交易策略
def checkPolicy(stockCodeArray,stockName):
    #参数 ['date', 'code', 'open', 'high', 'low', 'close', 'dw', 'w', '增幅', 'ma5', 'ma10', 'ma110', 'Cma10', 'ma5VsMa10', 'ma5动态', 'ma10动态', '双向上',
    # '大于ma110', 'ma5向上价', 'ma10向上价', 'ma双向上价', '双向上最低升幅', 'ma双向上价K线内', 'ma双向上价/10日线', 'ma双向上价/收盘价', '最低价/ma双向上价', '最高价/ma双向上价',
    # 'k', 'd', 'j', 'kTrend', 'jTrend', 'k50', 'j20', 'ema12', 'ema26', 'dif', 'dea', 'bar', 'deaHL', 'barHL', 'bTrend', 'barKey', 'deaP', 'difGrowth', 'difGP',
    # 'deaGrowth', 'deaGP', 'po', 'date_W', 'code_W', 'open_W', 'high_W', 'low_W', 'close_W', '增幅_W', 'po_W', 'ema12_W', 'ema26_W', 'dif_W', 'dea_W', 'bar_W', 'deaHL_W',
    # 'barHL_W', 'bTrend_W', 'barKey_W', 'k_W', 'd_W', 'j_W', 'kTrend_W', 'jTrend_W', 'k50_W', 'j20_W', '加分_W', '减分_W', '加分描述_W', '减分描述_W', 'deaTrend_W',
    # 'barRankP_W', 'bNo_W', 'barKey_H', '加分', '减分', '加分描述', '减分描述', 'bNo', 'barKeyCh', 'poValue', 'pEma26']

    ##周数据处理#####
    dfWeekArray = getFileOnLocalWeek(stockCodeArray, stockName)  # 把周线数据单独处理和输出

    # 策略 ：

    # 策略：单纯根据周股价偏离程度排序（周线比日线偏离更大），捕捉哪些短期反弹行情
    result = getWeekPriceDifEma26(dfWeekArray, stockName)

    # 策略：根据周bar值， 0线下bar转向上次数和偏离通道程度，捕捉哪些反弹的股票

    # 策略： 根据周bar值，0线上bar转向下次数和偏离通道程度，捕捉哪些持续上升的股票



    ##日数据处理#####

    # #判断本地是否有processFor处理后的文件，如果有直接读取； 否则调用processFor来生成文件导出到本地
    dfArray = getFileOnLocal(stockCodeArray, stockName)

    # #取股票最近N日k线数据，方便查看
    result = getKline(dfArray, stockName)



    # 通过止损点来设计交易策略
    # 遇到止损点，计算左边最高价，直到右边等于左边最高价时买入。买入后在下一个止损点卖出
    # result = buyPolicyLossStop(dfArray,stockName)

    # 针对向上行情（周线ema12向上），用通道和止损策略买卖，当买时也要看看macd bar值情况
    # result = buyPolicyWeekEma12up(dfArray,stockName)

    # 趋势交易法可能适用这个
    # 当bar为负，找某天哪些假向上最多当股票，给他们排序，看看排前面转真向上的概率是不是大些.. 感觉这个方法可能对于发现新趋势有帮助，一旦趋势形成持有就可以
    # result = getBarChangeMaxStock(dfArray,stockName)
    # 补充周线
    # result = getBarChangeMaxStockWeekly(dfArray,stockName)

    # 当bar为正是，同理可以统计假向下

    # 检查kdj的J值，J值在20一下向上或上穿20，开始监控，日线周线的情况
    # result = buyPolicyKdjUp20(dfArray,stockName)

    ##根据周线bar柱的切换来判断买入
    # result = buyPolicyBarChange(dfArray,stockName)

    # 根据macd Bar值趋势和长短周期的判断方法
    # result =  buyPolicyMacdBarKey(dfArray,stockName)

    # 策略：用kdj、ma100、日macd趋势、周macd趋势来识别买点
    # result = buyPolicyMacdKdj(dfArray,stockName)




    return



#为节约调试时所需时间，把数据放在本地
# def getFileOnLocalAll(stockCodeArray, stockName):
#     #在本地是否存在股票的csv文件，文件名为getOnlyKline_2_2020-12-20,中间数字为该次去股票的个数
#     today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
#     fileType = 'processFor'
#     if len(stockCodeArray) == 1:
#         fileName = fileType + '_' + stockCodeArray[0] + '_' + today
#         # fileName = fileType + '_' + stockCodeArray[0] + '_' + today + '.csv'
#     else:
#         fileName = fileType + '_' + str(len(stockCodeArray)) + '_' + today
#         # fileName = fileType + '_' + str(len(stockCodeArray)) + '_' + today + '.csv'
#     filePath = "/Users/miketam/Downloads/" + fileName
#
#     if os.path.exists(filePath+'.csv'):
#         #从本地去
#         df = pd.read_csv(filePath + '.csv',sep=',',encoding="gb2312", dtype={'barKey': str,'barKey_W':str})
#     else:
#         df = processFor(stockCodeArray,1,stockName,filePath)
#     dfArray = dfDivide(stockCodeArray,df)
#     return dfArray


# def getFilePath(stockCodeArray,  ft = 'processDay'):
#     today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
#     fileType = ft
#     if len(stockCodeArray) == 1:
#         fileName = fileType + '_' + stockCodeArray[0] + '_' + today
#         # fileName = fileType + '_' + stockCodeArray[0] + '_' + today + '.csv'
#     else:
#         fileName = fileType + '_' + str(len(stockCodeArray)) + '_' + today
#         # fileName = fileType + '_' + str(len(stockCodeArray)) + '_' + today + '.csv'
#     filePath = "/Users/miketam/Downloads/" + fileName
#     return filePath


#为节约调试时所需时间，把数据放在本地
def getFileOnLocalWeek(stockCodeArray, stockName):
    #在本地是否存在股票的csv文件，文件名为getOnlyKline_2_2020-12-20,中间数字为该次去股票的个数

    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    # fileType = 'processFor'
    fileType = 'processWeek'
    if len(stockCodeArray) == 1:
        fileName = fileType + '_' + stockCodeArray[0] + '_' + today
        # fileName = fileType + '_' + stockCodeArray[0] + '_' + today + '.csv'
    else:
        fileName = fileType + '_' + str(len(stockCodeArray)) + '_' + today
        # fileName = fileType + '_' + str(len(stockCodeArray)) + '_' + today + '.csv'
    filePath = "/Users/miketam/Downloads/" + fileName
    if os.path.exists(filePath+'.csv'):
        #从本地去
        df = pd.read_csv(filePath + '.csv',sep=',',encoding="gb2312", dtype={'barKey': str,'barKey_W':str})
        # df = pd.read_csv(filePath + '.csv',sep=',',encoding="gb2312", dtype={'barKey': str,'barKey_W':str},converters={'增幅':p2f})
    else:
        # df = processFor(stockCodeArray,1,stockName,filePath)
        df = processKline(stockCodeArray, type = 'week')[1] #只要周线
        df.to_csv(filePath + ".csv", encoding="gbk", index=False)
        df.to_excel(filePath + '.xlsx', float_format='%.5f', index=False)
    dfArray = dfDivide(stockCodeArray,df)
    return dfArray

def p2f(x):
    return float(x.strip('%'))/100

#为节约调试时所需时间，把数据放在本地
def getFileOnLocal(stockCodeArray, stockName):
    #在本地是否存在股票的csv文件，文件名为getOnlyKline_2_2020-12-20,中间数字为该次去股票的个数
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    fileType = 'processFor'
    if len(stockCodeArray) == 1:
        fileName = fileType + '_' + stockCodeArray[0] + '_' + today
        # fileName = fileType + '_' + stockCodeArray[0] + '_' + today + '.csv'
    else:
        fileName = fileType + '_' + str(len(stockCodeArray)) + '_' + today
        # fileName = fileType + '_' + str(len(stockCodeArray)) + '_' + today + '.csv'
    filePath = "/Users/miketam/Downloads/" + fileName
    if os.path.exists(filePath+'.csv'):
        #从本地去
        df = pd.read_csv(filePath + '.csv',sep=',',encoding="gb2312", dtype={'barKey': str,'barKey_W':str})
    else:
        df = processFor(stockCodeArray,1,stockName,filePath)
    dfArray = dfDivide(stockCodeArray,df)
    return dfArray




#数据处理，主要通过for循环来处理数据
def processFor(stockCodeArray, toFile, stockNameArray, filePath):

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
                # print(df[['date', 'close', '增幅', 'ma10', 'Cma10', 'ma5动态', 'ma10动态', '双向上', 'barRank', 'barRankP','deaHL', 'deaTrend', 'deaPRank', 'deaGTS', 'deaGPRank', 'buy2', 'sell', 'sell2']])
                df = df[['code','date', 'close', '增幅', 'ma10', 'Cma10', 'ma5动态', 'ma10动态', '双向上', 'barRank', 'barRankP','deaHL', 'deaTrend', 'deaPRank', 'deaGTS', 'deaGPRank', 'buy2', 'sell', 'sell2']]
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
    dfKline = processKline(stockCodeArray, type = 'all', toFile=toFile)

    dfday = dfKline[0] #取日线数据
    dfweek = dfKline[1] #取周线数据
    # dfMonth = dfKline[2] #取周线数据
    # dfhour = dfKline[2]

    dfDayArray = dfDivide(stockCodeArray,dfday) #把df拆分，每个股票一个df
    dfweekArray = dfDivide(stockCodeArray,dfweek) #把df拆分，每个股票一个df
    # dfMonthArray = dfDivide(stockCodeArray,dfMonth) #把df拆分，每个股票一个df
    # dfhourArray = dfDivide(stockCodeArray,dfhour) #把df拆分，每个股票一个df

    resultArray = []
    dfAppend: DataFrame = pd.DataFrame()

    #处理每一个股票的df
    for x in range(len(dfDayArray)):
        df = dfDayArray[x]
        dfweek = dfweekArray[x]
        # dfhour = dfhourArray[x]
        df['po'] = ''

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
        dfweek = dfweek.drop([len(dfweek) - 1])  #因为dfweek最后一天在处理止损价时生成，这里要删除
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
        barChangeCount = 0
        ema26DiffArray = np.array([])
        lowDiffArray = np.array([])
        lowDifEma26Array = np.array([])
        highDifEma26Array = np.array([])


        index = len(df) - 1 #得到索引,减1是因为之前增加一个不规则的行数据
        barHLidList = df.loc[(df.barHL == 'H') | (df.barHL == 'L')].index.tolist() #bar所有HL点的的行的索引


        #这个循环效率，日后可以优化
        for i in range(index):
            code = df.at[0,'code']


            # #估计bar值所在波形的位置
            df = getBarPositionDf(barHLidList,df,i)  #里面的describe函数很慢
            #计算得分
            # df = getScore(df,i,'d')

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


            # #识别当前点的DEA、dif是向上或向下
            # # df = getMacdTrend(i,df,'deaHL','deaTrend')
            # # df = getMacdTrend(i,df,'difHL','difTrend')
            # df = getDeaDifTrend(i,df,'deaHL','deaTrend') #里面rank值是本周期内(bar值周期内排序在里面）
            # # df = getDeaDifTrend(i,df,'difHL','difTrend')
            #
            #
            # #处理bar值的半年排序
            # value = getValueRank(i,df,'bar','barRank',array,250,'start')
            # df = value[0]
            # array =value[1]
            #
            # # 处理dea/Price的排序
            # value = getValueRank(i,df,'deaP','deaPRank',array3, 250,'start')
            # df = value[0]
            # array3 =value[1]
            #
            #
            # #处理deaGrowth/Price的排序
            # value = getValueRank(i,df,'deaGP','deaGPRank',array2, 250,'start')
            # df = value[0]
            # array2 =value[1]
            #
            #
            #
            # #处理deaGrowth/Price的排序
            # value = getValueRank(i,df,'dea','deaRank',array2, 250,'start')
            # df = value[0]
            # array4 =value[1]
            #
            # #识别dea增量趋势、dif增量趋势
            # temp = []
            # if i > 2:
            #     for x in range(-2,1):
            #         temp.append(abs(df.at[i+x,'deaGrowth']))
            #     df.at[i, 'deaGrowthTrend'] = trendline(temp)
            #     if trendline(temp) > 0:
            #         df.at[i, 'deaGTS'] = '加速'
            #     else:
            #         df.at[i, 'deaGTS'] = ''
            #
            # temp = []
            # if i > 2:
            #     for x in range(-2,1):
            #         temp.append(abs(df.at[i+x,'difGrowth']))
            #     df.at[i, 'difGrowthTrend'] = trendline(temp)
            #     if trendline(temp) > 0:
            #         df.at[i, 'difGTS'] = '加速'
            #     else:
            #         df.at[i, 'difGTS'] = ''



            # 把周线数据写入日线列表
                #找到当前日线对应的周线，把数据复制过去
            dayYearWeek = getYearWeekFromDate(df.iat[i,0]) #找到某天对应到年份+周数
            if dayYearWeek in week:
                p = week.index(dayYearWeek)
                # df.loc[i, columnNameList[0]:columnNameList[len(columnNameList) - 1]] = dfweek.iloc[p]
                df.iloc[i, weekDataBegin:weekDataEnd] = dfweek.iloc[p]  #上行也可以，差别只是定位方式不一样


                #用日数据更新当天的周数据，比如ema，macd等
                if p > 0:
                    # df.at[i,'ema12_W2'] = getEMA(12, dfweek.at[p-1,'ema12_W'], df.at[i,'close'])  #这个是按日向上，原来ema12_W是按周显示
                    # df.at[i,'ema12Trend_W2'] = np.where(df.at[i,'ema12_W2'] > dfweek.at[p-1,'ema12_W'],'up','down')
                    # df.at[i,'ema26_W2'] = getEMA(26, dfweek.at[p-1,'ema26_W'], df.at[i,'close'])
                    #还可以补充，包括脉冲系统，等需要这些数据回测时再计算
                    previousEMA12 = dfweek.at[p-1,'ema12_W']
                    previousEMA26 = dfweek.at[p-1,'ema26_W']
                    previousDEA = dfweek.at[p-1,'dea_W']
                    closePrice = df.at[i,'close']
                    df.at[i,'bar_W2'] = getMacd(previousEMA12,previousEMA26,previousDEA,closePrice)[2] #每天更新周bar值
                    #每天更新周bar值的转向（若当天的动态周bar值相对上周是向上，就标记为1，还有前一周也符合条件）
                    if p > 1:
                        df.at[i,'bar021_W2'] = np.where(
                            (dfweek.at[p-2,'bar_W'] > dfweek.at[p-1,'bar_W']) & (df.at[i,'bar_W2'] > dfweek.at[p-1,'bar_W']) & (dfweek.at[p-1,'bar_W'] < 0), 1,
                            np.nan)

                    #
                    # df['bar021'] = np.where(
                    #     (df['bar'].shift(-1) > df['bar']) & (df['bar'].shift(1) > df['bar']) & (df['bar'] < 0), df['bar'],
                    #     np.nan)

            # #把小时线数据写入列表
            # date = df.at[i,'date']
            # dfDayHour = dfhour.loc[dfhour['date']==date] #把今天的小时k线取出
            # barKeyArray = dfDayHour['barKey'].tolist()
            # # df.at[i, 'barKey_H'] = barKeyArray
            # temp = ''
            # for m in barKeyArray:
            #     temp = temp + m
            # df.at[i,'barKey_H'] = temp #


            #买策略：利用macd到dea和bar的高点变化来给出买点
            # df = buyPolicyMacdTrend(i, df)



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
        # print(df)
        # print('33')
        # exit()
        df = getPulseSystem(df) #
        df = getATRChannel(df) #生成ATR通道
        #做一下ATR通道预测
        # df = df[['date','code','ATR1','ATR2','ATR3','ATR-1','ATR-2','ATR-3',]]



        resultStr = '股票：' +code + '，购买次数：' + str(buycount)  + "，盈利次数：" + str(wincount) + "，亏损次数：" + str(losscount),'因macd少盈利：' + str(winReduce) +\
                 ', 因macd少亏损：' + str(lossReduce) + ', 实际盈利：'+ str(wincount-winReduce) + ', 实际亏损：' + str(losscount - lossReduce)
        resultArray.append(resultStr)
        dfAppend = dfAppend.append(df)


    #在这里可以屏蔽一些列，减少导出数据的容量
    # colsHide = ['code','date']
    # cols = [i for i in dfAppend.columns if i not in colsHide]
    # dfAppend = dfAppend[cols]


        # print(df[['date','bar','barRank','deaHL','deaTrend','difHL','difTrend']])
        # print(df[['date','bar','barRank','deaHL','dea','deaTrend','deaGrowthTrend','deaGrowthTrendSign','deaGP','deaGPRank','deaPRank']])
        # print(df[['date','close','bar','barRank','barRankP','deaHL','deaTrend','difHL','difTrend','difGrowthTrend','difGrowthTrendSign','deaGP','deaGPRank','deaPRank','buy','buy2','sell','sell2']])
        # print(df[['date','bar','barRank','deaHL','deaTrend','difHL','difTrend','difGrowth','difGP','deaGrowth','deaGrowthTrend','deaGP']])

        # print(df[['date','close','增幅','大于ma110','双向上','barRank','barRankP','deaHL','deaTrend','deaPRank','deaGTS','deaGPRank','k','kTrend','k50','buy2','sell','sell2']])
        # print(df[['date','close','k','d']])
        # print(df[['barHL_W','bTrend_W','po_W','bNo_W','date','close','增幅','大于ma110','双向上','barHL','bTrend','po','bNo','barRank','barRankP','k','kTrend','k50','buy2','sell','sell2']])
        # print(df[['barHL_W','bTrend_W','po_W','bNo_W','date','dw','w','close','增幅','大于ma110','双向上','barHL','bTrend','po','bNo','barRank','barRankP','k','kTrend','k50','buy2','sell','sell2']])
        # exit()
        # print(df[[0,'deaHL','deaTrend','barRankP','bar','barHL','bTrend','po','bNo']])

    path = filePath
    dfAppend.to_csv(path + ".csv", encoding="gbk", index=False)
    dfAppend.to_excel(path + '.xlsx', float_format='%.5f',index=False)

    # dfAppend.to_csv("/Users/miketam/Downloads/checkPolicy.csv", encoding="gbk", index=False)
    # dfAppend.to_excel('/Users/miketam/Downloads/checkPolicy.xlsx', float_format='%.5f',index=False)
    return dfAppend
    # for i in resultArray:
    #     print(i)
    # print(dfAppend.dtypes)

