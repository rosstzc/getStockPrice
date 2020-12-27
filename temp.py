import baostock as bs
import pandas as pd
import openpyxl
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
from func import *
from buyAndSellPolicy import *

pd.set_option('display.width', 210)
pd.set_option('display.max_columns', 130)
pd.set_option('display.max_colwidth', 130)
pd.set_option('display.max_rows', None)


# def processDataBefore


# 策略测试
def checkPolicy(stockCodeArray, toFile, stockNameArray):
    # 石基信息(SZ: 002153)，中环股份(SZ:002129)，上海莱士(SZ:002252)

    # 拆分checkPolicy处理后csv大文件，然后按股票代码生成单个csv文件
    if toFile == 2:
        df = pd.read_csv('/Users/miketam/Downloads/checkPolicy_300.csv', sep=',', encoding="gb2312")
        # df = pd.read_csv('/Users/miketam/Downloads/getOnlyKline.csv', header=None, sep=',')
        dfArray = dfDivide(stockCodeArray, df)
        dfArrayNew = []
        rank = 0.4  # barRank排名百分比
        x = 0
        for df in dfArray:
            # if abs(str2Float(df.at[-2,'barRank'])) < 0.4 or abs(str2Float(df.at[-3,'barRank']))< 0.4 or abs(str2Float(df.at[-4,'barRank'])) < 0.4:
            if abs(str2Float(df.iloc[-2]['barRank'])) < rank or abs(str2Float(df.iloc[-3]['barRank'])) < rank:
                # print(df[['date', 'close', '增幅', 'ma10', 'Cma10', 'ma5动态', 'ma10动态', '双向上', 'barRank', 'barRankPeriod','deaHL', 'deaTrend', 'deaPRank', 'deaGTS', 'deaGPRank', 'buy2', 'sell', 'sell2']])
                df = df[['code', 'date', 'close', '增幅', 'ma10', 'Cma10', 'ma5动态', 'ma10动态', '双向上', 'barRank',
                         'barRankPeriod', 'deaHL', 'deaTrend', 'deaPRank', 'deaGTS', 'deaGPRank', 'buy2', 'sell',
                         'sell2']]
                code = df.iloc[-2]['code']
                stockName = stockNameArray[x]
                url = '/Users/miketam/Downloads/checkPolicy/' + code + '.csv'
                urlXlsx = '/Users/miketam/Downloads/checkPolicy/' + stockName + '_' + code + '.xlsx'
                # df.to_csv(url, encoding="gbk", index=False)
                df.to_excel(urlXlsx, float_format='%.5f', index=False)
                dfArrayNew.append(df)
            x = x + 1
        return dfArrayNew

    # 根据策略处理数据
    dfTemp = processKline(stockCodeArray, toFile=toFile)
    dfArray = dfDivide(stockCodeArray, dfTemp)  # 把df拆分，每个股票一个df

    resultArray = []
    dfAppend: DataFrame = pd.DataFrame()

    # 处理每一个股票的df
    for df in dfArray:
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
        winReduce = 0  # 根据macd减少盈利次数
        losscount = 0
        lossReduce = 0  # 根据macd减少损失次数
        winPrecent = 0.04
        lossPrecent = 0.04
        array = []
        array2 = []
        array3 = []
        array4 = []

        index = len(df) - 1  # 得到索引
        # 这个循环效率，日后可以优化
        for i in range(index):
            code = df.at[0, 'code']

            # 识别当前点的DEA、dif是向上或向下
            # df = getMacdTrend(i,df,'deaHL','deaTrend')
            # df = getMacdTrend(i,df,'difHL','difTrend')
            df = getDeaDifTrend(i, df, 'deaHL', 'deaTrend')
            # df = getDeaDifTrend(i,df,'difHL','difTrend')

            # 处理bar值的半年排序
            value = getValueRank(i, df, 'bar', 'barRank', array, 250, 'start')
            df = value[0]
            array = value[1]

            # 处理bar值的周期排序（每个波动周期重新排序）

            # 处理dea/Price的排序
            value = getValueRank(i, df, 'deaP', 'deaPRank', array3, 250, 'start')
            df = value[0]
            array3 = value[1]

            # 处理deaGrowth/Price的排序
            value = getValueRank(i, df, 'deaGP', 'deaGPRank', array2, 250, 'start')
            df = value[0]
            array2 = value[1]

            # 处理deaGrowth/Price的排序
            value = getValueRank(i, df, 'dea', 'deaRank', array2, 250, 'start')
            df = value[0]
            array4 = value[1]

            # 识别dea增量趋势、dif增量趋势
            temp = []
            if i > 2:
                for x in range(-2, 1):
                    temp.append(abs(df.at[i + x, 'deaGrowth']))
                df.at[i, 'deaGrowthTrend'] = trendline(temp)
                if trendline(temp) > 0:
                    df.at[i, 'deaGTS'] = '加速'
                else:
                    df.at[i, 'deaGTS'] = ''

            temp = []
            if i > 2:
                for x in range(-2, 1):
                    temp.append(abs(df.at[i + x, 'difGrowth']))
                df.at[i, 'difGrowthTrend'] = trendline(temp)
                if trendline(temp) > 0:
                    df.at[i, 'difGTS'] = '加速'
                else:
                    df.at[i, 'difGTS'] = ''

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

            # resultTemp = buyPolicyMacd1(df, buyState, buycount, buyIndex, buyPrice, i, array)

            # 买入策略1
            # buy = buyPolicy1(df, buyState, buycount, buyIndex, buyPrice, i)
            # df = buy[0]
            # buyState = buy[1]
            # buycount = buy[2]
            # buyIndex = buy[3]
            # buyPrice = buy[4]

            # 买入后，刷新买入价与每天高低价的比较
            if buyState == 1:
                a = df.at[i, 'low']
                b = buyPrice
                df.at[i, '最低价/买入'] = format(df.at[i, 'low'] / buyPrice - 1, '.2%')
                df.at[i, '最高价/买入'] = format(df.at[i, 'high'] / buyPrice - 1, '.2%')

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

        resultStr = '股票：' + code + '，购买次数：' + str(buycount) + "，盈利次数：" + str(wincount) + "，亏损次数：" + str(
            losscount), '因macd少盈利：' + str(winReduce) + \
                    ', 因macd少亏损：' + str(lossReduce) + ', 实际盈利：' + str(wincount - winReduce) + ', 实际亏损：' + str(
            losscount - lossReduce)
        resultArray.append(resultStr)
        dfAppend = dfAppend.append(df)

        # print(df[['date','bar','barRank','deaHL','deaTrend','difHL','difTrend']])
        # print(df[['date','bar','barRank','deaHL','dea','deaTrend','deaGrowthTrend','deaGrowthTrendSign','deaGP','deaGPRank','deaPRank']])
        # print(df[['date','close','bar','barRank','barRankPeriod','deaHL','deaTrend','difHL','difTrend','difGrowthTrend','difGrowthTrendSign','deaGP','deaGPRank','deaPRank','buy','buy2','sell','sell2']])
        # print(df[['date','bar','barRank','deaHL','deaTrend','difHL','difTrend','difGrowth','difGP','deaGrowth','deaGrowthTrend','deaGP']])

        # print(df[['date','close','增幅','ma10','Cma10','ma5动态','ma10动态','双向上','barRank','barRankPeriod','deaHL','deaTrend','deaPRank','deaGTS','deaGPRank','buy2','sell','sell2']])
        print(df[['date', 'close', 'k', 'd']])

        exit()

    dfAppend.to_csv("/Users/miketam/Downloads/checkPolicy.csv", encoding="gbk", index=False)
    dfAppend.to_excel('/Users/miketam/Downloads/checkPolicy.xlsx', float_format='%.5f', index=False)
    # for i in resultArray:
    #     print(i)
    # print(dfAppend.dtypes)


# 计算周线都各种数据，比如macd,kdj
def getWeeklyData(kLineWeekArray):
    dfAppend: DataFrame = pd.DataFrame()  #
    for x in kLineWeekArray:
        df: DataFrame = pd.DataFrame(x)
        df[2] = pd.to_numeric(df[2])  # 开盘价，把字符转化为数字
        df[3] = pd.to_numeric(df[3])  # 最高价，把字符转化为数字
        df[4] = pd.to_numeric(df[4])  # 最低价，把字符转化为数字
        df[5] = pd.to_numeric(df[5])  # 收盘价，把字符转化为数字
        df = getDfMacd(df)  # 获取macd
        df = getDfKdj(df)  # 获取kdj
        df.rename(columns={
            0: 'date',
            1: 'code',
            2: 'open',
            3: 'high',
            4: 'low',
            5: 'close',
        }, inplace=True)

        # 计算dea的HL点

        # 计算dea的向上、向下趋势

        # 计算bar值在本周期的百分比

        dfAppend = dfAppend.append(df)
    return dfAppend


# K线数据二次加工
def processKline(stockCodeArray, toFile=1):
    kLineArray = getOnlyKline(stockCodeArray, toFile)[0]
    kLineWeekArray = getOnlyKline(stockCodeArray, toFile)[1]  # 周k线
    dfAppend: DataFrame = pd.DataFrame()
    # 要获取的值：
    # 收盘数据：ma5，ma10，ma5动态，ma10动态，ma5是否大于ma10，是否双向上(含实时动态)，双向上最低价格，双向上价是否在高低范围内，ma10通道，收盘价相对ma5，ma10明天预测，ma10明天预测动态； 更多均线：20，30，60
    # macd:快线值、慢行值，快线动态，慢线动态
    # 实时数据：某个股价时，以上的数据再来一遍
    # 针对ema，上面数据再来一遍
    # 周线数据：周ma5...

    # 计算周线的各种数据，最后合并为一个大df
    dfWeekAppend = getWeeklyData(kLineWeekArray)

    # 取出每个股票的k线数据，每个i代表1个股票的所有K线
    for x in kLineArray:
        kLineDf: DataFrame = pd.DataFrame(x)
        # kLineDf.columns = ["date", "code", "open", "high", "low", "close"]
        # 添加均线
        kLineDf[2] = pd.to_numeric(kLineDf[2])  # 开盘价，把字符转化为数字
        kLineDf[3] = pd.to_numeric(kLineDf[3])  # 最高价，把字符转化为数字
        kLineDf[4] = pd.to_numeric(kLineDf[4])  # 最低价，把字符转化为数字
        kLineDf[5] = pd.to_numeric(kLineDf[5])  # 收盘价，把字符转化为数字

        kLineDf["增幅"] = kLineDf[5] / kLineDf[5].shift() - 1
        kLineDf["增幅"] = kLineDf["增幅"].apply(lambda x: format(x, '.2%'))
        kLineDf["ma5"] = kLineDf[5].rolling(window=5).mean()  # 5日线
        kLineDf["ma10"] = kLineDf[5].rolling(window=10).mean()  # 10日线
        kLineDf["ma100"] = kLineDf[5].rolling(window=100).mean()  # 100

        kLineDf["Cma10"] = kLineDf[5] / kLineDf["ma10"] - 1
        kLineDf["Cma10"] = kLineDf["Cma10"].apply(lambda x: format(x, '.2%'))

        kLineDf["ma5VsMa10"] = np.where(kLineDf['ma5'] > kLineDf['ma10'], "大于", "")  # 两均线比较

        # kLineDf["ma20"] = kLineDf[5].rolling(window=20).mean()  # 10日线

        # 均线动态(收盘价)
        kLineDf["ma5Trend"] = np.where(kLineDf['ma5'] > kLineDf['ma5'].shift(+1), "向上", "")
        kLineDf["ma10Trend"] = np.where(kLineDf['ma10'] > kLineDf['ma10'].shift(+1), "向上", "")

        # 5日线，10日线是否双向上
        kLineDf["ma5ma10Trend"] = np.where((kLineDf["ma5Trend"] == "向上") & (kLineDf["ma10Trend"] == "向上"), "是", "")

        new = ['用双向上基线做的预测值']  # 新增一行，方便显示均线向上的最低值。一定要价true这个参数
        kLineDf = kLineDf.append(new, ignore_index=True)

        # 计算最低向上价格。把df列变为数组，在数组运算后再变为df
        closePriceArray = kLineDf[5].values
        ma5Array = kLineDf["ma5"].values
        ma10Array = kLineDf["ma10"].values
        kLineDf["priceForMa5Up"] = getPriceForMaUp(5, closePriceArray, ma5Array)
        kLineDf["priceForMa10Up"] = getPriceForMaUp(10, closePriceArray, ma10Array)
        kLineDf["priceForMa5Ma10Up"] = np.where(kLineDf["priceForMa5Up"] > kLineDf["priceForMa10Up"],
                                                kLineDf["priceForMa5Up"], kLineDf["priceForMa10Up"])  # 双向上最低价
        kLineDf["growthForpriceForMa5Ma10Up"] = kLineDf["priceForMa5Ma10Up"] / kLineDf[5].shift() - 1
        kLineDf["growthForpriceForMa5Ma10Up"] = kLineDf["growthForpriceForMa5Ma10Up"].apply(lambda x: format(x, '.2%'))

        # #给双向上指标增加动态
        kLineDf["ma5ma10Trend"] = np.where(
            (kLineDf["ma5ma10Trend"] == '是') & (kLineDf[4] < kLineDf["priceForMa5Ma10Up"]), '是，有向下',
            kLineDf["ma5ma10Trend"])
        kLineDf["ma5ma10Trend"] = np.where(
            (kLineDf["ma5ma10Trend"] == '') & (kLineDf[3] > kLineDf["priceForMa5Ma10Up"]), '有双向上',
            kLineDf["ma5ma10Trend"])

        # 双向上价是否在K线内
        kLineDf["priceForMa5Ma10UpInKLine"] = np.where(
            (kLineDf[4] < kLineDf["priceForMa5Ma10Up"]) & (kLineDf["priceForMa5Ma10Up"] < kLineDf[3]), 'Y', '')

        # 把双向上基线放放到收盘价作为参考，并更新ma5、ma10作为参考
        index = len(kLineDf) - 1
        kLineDf.at[index, 5] = kLineDf.at[index, 'priceForMa5Ma10Up']
        kLineDf["ma5"] = kLineDf[5].rolling(window=5).mean()  # 再次更新一下均线
        kLineDf["ma10"] = kLineDf[5].rolling(window=10).mean()  # 再次更新一下均线
        kLineDf.at[index, 1] = x[0][1]

        # 双向上基线对比10日线
        kLineDf["priceForMa5Ma10UpVsMa10"] = kLineDf["priceForMa5Ma10Up"] / kLineDf["ma10"] - 1
        kLineDf["priceForMa5Ma10UpVsMa10"] = kLineDf["priceForMa5Ma10UpVsMa10"].apply(lambda x: format(x, '.2%'))

        ##双向上价/收盘价
        kLineDf["priceForMa5Ma10UpVsClosePrice"] = kLineDf["priceForMa5Ma10Up"] / kLineDf[5] - 1
        kLineDf["priceForMa5Ma10UpVsClosePrice"] = kLineDf["priceForMa5Ma10UpVsClosePrice"].apply(
            lambda x: format(x, '.2%'))

        # kLineDf["priceForMa5Ma10UpVsLowPrice"] #最低价/双向上价
        kLineDf["lowPriceVsPriceForMa5Ma10Up"] = kLineDf[4] / kLineDf["priceForMa5Ma10Up"] - 1
        kLineDf["lowPriceVsPriceForMa5Ma10Up"] = kLineDf["lowPriceVsPriceForMa5Ma10Up"].apply(
            lambda x: format(x, '.2%'))

        # kLineDf["priceForMa5Ma10UpVsHighPrice"] #最高价/双向上价
        kLineDf["highPriceVsPriceForMa5Ma10Up"] = kLineDf[3] / kLineDf["priceForMa5Ma10Up"] - 1
        kLineDf["highPriceVsPriceForMa5Ma10Up"] = kLineDf["highPriceVsPriceForMa5Ma10Up"].apply(
            lambda x: format(x, '.2%'))

        # 计算kdj
        kLineDf = getDfKdj(kLineDf)

        # # #MACD相关
        kLineDf = getDfMacd(kLineDf)

        # 判断dif、dea波浪线高低点
        kLineDf['difHL'] = np.where(
            (kLineDf['dif'] - kLineDf['dif'].shift(1) >= 0) & (kLineDf['dif'] - kLineDf['dif'].shift(-1) >= 0), 'H',
            kLineDf['dif'])
        kLineDf['difHL'] = np.where(
            (kLineDf['dif'] - kLineDf['dif'].shift(1) <= 0) & (kLineDf['dif'] - kLineDf['dif'].shift(-1) <= 0), 'L',
            kLineDf['difHL'])
        kLineDf['deaHL'] = np.where(
            (kLineDf['dea'] - kLineDf['dea'].shift(1) >= 0) & (kLineDf['dea'] - kLineDf['dea'].shift(-1) >= 0), 'H',
            kLineDf['dea'])
        kLineDf['deaHL'] = np.where(
            (kLineDf['dea'] - kLineDf['dea'].shift(1) <= 0) & (kLineDf['dea'] - kLineDf['dea'].shift(-1) <= 0), 'L',
            kLineDf['deaHL'])

        # 计算dea/price
        kLineDf['deaP'] = kLineDf['dea'] / kLineDf[5] * 100

        # 计算增量（今天减昨天）、增量/股价比，然后转化为百分数
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
            'closeEma': '收盘价EMA用',
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

        dfAppend = dfAppend.append(kLineDf)  # 带上自己的索引
        # dfAppend = dfAppend.append(kLineDf,ignore_index=True)
        ### 结果集输出到csv文件 ####
    if toFile == 1:
        # dfAppend.to_csv("/Users/miketam/Downloads/processKline.csv", encoding="gbk")
        dfAppend.to_csv("/Users/miketam/Downloads/processKline.csv", encoding="gbk", index=False)
        # macd.to_csv("/Users/miketam/Downloads/processKline_macd.csv", encoding="gbk", index=False)
        # print(dfAppend)
        # dfAppend.to_excel('/Users/miketam/Downloads/processKline.xlsx', float_format='%.5f',index=False)
    return dfAppend


# 获取周K线，然后再计算周macd
def getWeeklyKline(stockCodeArray, start_date, end_date):
    klineWeekArray = []
    for i in stockCodeArray:
        data_list = []
        code = codeFormat(i)
        rs = bs.query_history_k_data_plus(code,
                                          # 0    1     2    3   4    5      6       7      8        9      10     11          12    13    14    15      16     17
                                          # "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                                          "date,code,open,high,low,close",
                                          start_date=start_date, end_date=end_date,
                                          frequency="w", adjustflag="2")
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
        klineWeekArray.append(data_list)
    return klineWeekArray


# 获取最基础到K线数据
def getOnlyKline(stockCodeArray, toFile=1, start_date='2018-01-06', end_date='2023-10-31'):
    # 如果toFile=0就直接读取本地csv文件
    if toFile == 0:
        df = pd.read_csv('/Users/miketam/Downloads/getOnlyKline_300.csv', sep=',')
        # df = pd.read_csv('/Users/miketam/Downloads/getOnlyKline.csv', header=None, sep=',')
        # 得先把数据按股票拆分为一个个array，每个股票的k线是一个array
        dfArray = dfDivide(stockCodeArray, df)
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
                                          "date,code,open,high,low,close",
                                          start_date=start_date, end_date=end_date,
                                          frequency="d", adjustflag="2")
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())

        # 去掉停牌的日期的数据
        temp_list = []
        for i in range(len(data_list)):
            if data_list[i][5] != data_list[i - 1][5] or data_list[i][3] != data_list[i - 1][3] and i > 0:
                temp_list.append(data_list[i])
        data_list = temp_list

        arrayMerage.extend(data_list)
        klineArray.append(data_list)  # 用在二次处理
    result: DataFrame = pd.DataFrame(arrayMerage)
    result.columns = ["date", "code", "open", "high", "low", "close"]

    # 获取周K线数据
    KlineWeekArray = getWeeklyKline(stockCodeArray, start_date, end_date)

    if toFile == 1:
        result.to_excel('/Users/miketam/Downloads/getOnlyKline.xlsx', float_format='%.5f', index=False)
        result.to_csv("/Users/miketam/Downloads/getOnlyKline.csv", encoding="gbk", index=False)
        # print(result)
    return [klineArray, KlineWeekArray]


# 获取均线动态
def getMaLineTrend(stockCodeArray, stockNameArray):
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
        # 添加均线
        result[6] = result[5].rolling(window=5).mean()  # 5日线
        result[7] = result[5].rolling(window=10).mean()  # 10日线
        # result[8] = result[5].rolling(window=20).mean()  # 10日线
        # result.columns = ["date","code","open","high","low","close","ma5","ma10","ma20"]

        # 判断均线向上向下
        array = result.values  # 转为数组
        ma5 = ""
        ma10 = ""
        maArrayOneStock = []
        # maArray = []
        m = 0  # 双向下个数
        n = 0  # ma5向上
        for j in range(0, len(array)):  # 获取上一个，下一个
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

            maArrayOneDay = [Current[0], ma5, ma10]  # 后续日期做索引，df merge时不重复
            maArrayOneStock.append(maArrayOneDay)

        temp = pd.DataFrame(maArrayOneStock)
        temp.columns = ["date", stockName + "_ma5", str(i) + "_ma10"]
        # temp.set_index('date',inplace=True, drop=True)
        if x == 1:
            maMultiStockPd = temp
        else:
            maMultiStockPd = pd.merge(maMultiStockPd, temp, on='date')
    ### 结果集输出到csv文件 ####
    print(maMultiStockPd)
    # maMultiStockPd.to_csv("/Users/miketam/Downloads/getMaline.csv", encoding="gbk", index=False)
    maMultiStockPd.to_excel('/Users/miketam/Downloads/getMaline.xlsx', float_format='%.5f', index=False)
    return


