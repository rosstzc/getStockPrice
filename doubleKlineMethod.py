import baostock as bs
import pandas as pd
import openpyxl
import numpy as np
from pandas import DataFrame

from func import *





def checkPolicy(stockCodeArray):
    return



#K线数据二次加工
def processKline(stockCodeArray):
    kLineArray = getOnlyKline(stockCodeArray,0)

    # 要获取的值：
    # 收盘数据：ma5，ma10，ma5动态，ma10动态，ma5是否大于ma10，是否双向上(含实时动态)，双向上最低价格，双向上价是否在高低范围内，ma10通道，收盘价相对ma5，ma10明天预测，ma10明天预测动态； 更多均线：20，30，60
    # macd:快线值、慢行值，快线动态，慢线动态
    # 实时数据：某个股价时，以上的数据再来一遍
    # 针对ema，上面数据再来一遍
    # 周线数据：周ma5...

    #取出每个股票的k线数据，每个i代表1个股票的所有K线
    for x in kLineArray:
        kLineDf: DataFrame = pd.DataFrame(x)
        # kLineDf.columns = ["date", "code", "open", "high", "low", "close"]

        # 添加均线
        kLineDf["ma5"] = kLineDf[5].rolling(window=5).mean()  # 5日线
        kLineDf["ma10"] = kLineDf[5].rolling(window=10).mean()  # 10日线
        kLineDf["ma5VsMa10"] = np.where(kLineDf['ma5'] > kLineDf['ma10'] ,"大于","") #两均线比较

        #kLineDf["ma20"] = kLineDf[5].rolling(window=20).mean()  # 10日线

        kLineDf["ma5Trend"] = np.where( kLineDf['ma5'] > kLineDf['ma5'].shift(+1) ,"向上","")
        kLineDf["ma10Trend"] = np.where( kLineDf['ma10'] > kLineDf['ma10'].shift(+1) ,"向上","")
        kLineDf["test"] =  kLineDf["ma5"].shift(+1) + 100

        # #把df列变为数组，在数组运算后再变为df
        # closePriceArray = kLineDf[5].values
        # priceForMa5UpArray = []
        # for i in range(4, len(closePriceArray)):
        #     temp = 0
        #     for j in range(4):
        #         temp = temp + closePriceArray[i-j]
        #     temp2 = closePriceArray[i]*5 -temp + 0.01
        #     priceForMa5UpArray.append(temp2)
        # kLineDf["priceForMa5Up"] = pd.DataFrame(priceForMa5UpArray)

        # kLineDf["priceForMa5Up"] = #5日线向上的最低价
        # kLineDf["priceForMa10Up"] = #10日线向上的最低价
        # kLineDf["ma5ma10Trend"] #是否双向上（含动态）
        # kLineDf["priceForMa5Ma10Up"] #双向上最低价
        # kLineDf["priceForMa5Ma10UpInKineOrNot"] #双向上价是否在K线内
        # kLineDf["priceForMa5Ma10UpVsClosePrice"] #双向上价对比收盘价
        # kLineDf["priceForMa5Ma10UpVsLowPrice"] #双向上价对比最低价
        # kLineDf["priceForMa5Ma10UpVsHighPrice"] #双向上价对比最高价
        # kLineDf["priceForMa5Ma10UpVsMa10"] #双向上价对比10日线
        #
        # #实时价格
        # kLineDf["ma10RT"]  #在某股价时10均线值
        # kLineDf["ma10TrendRT"]  #在某股价时10均线动态
        #
        # #MACD相关
        # kLineDf["macd12"]
        # kLineDf["macd26"]
        # kLineDf["macdQuick"]
        # kLineDf["macdSlow"]
        #
        # #EMA相关
        # kLineDf["ema11"]
        # kLineDf["ema22"]
        # kLineDf["ema11Trend"]
        # kLineDf["ema22Trend"]
        # kLineDf["ema11ema12Trend"] #是否双向上（含动态）
        # kLineDf["priceForEma11Ema22Up"] #双向上最低价
        # kLineDf["priceForEma11Ema22UpInKineOrNot"] #双向上价是否在K线内
        # kLineDf["priceForEma11Ema22UpVsClosePrice"] #双向上价对比收盘价
        # kLineDf["priceForEma11Ema22UpVsLowPrice"] #双向上价对比最低价
        # kLineDf["priceForEma11Ema22UpVsHighPrice"] #双向上价对比最高价
        # kLineDf["priceForEma11Ema22UpVsMa10"] #双向上价对比10日线
        # #EMA实时
        # kLineDf["ema22RT"]  #在某股价时10均线值
        # kLineDf["ema22TrendRT"]  #在某股价时10均线动态
        #






        ### 结果集输出到csv文件 ####
        kLineDf.to_csv("/Users/miketam/Downloads/processKline.csv", encoding="gbk", index=False)
        print(kLineDf)

        kLineDf.to_excel('/Users/miketam/Downloads/processKline.xlsx', float_format='%.5f',index=False)



#获取最基础到K线数据
def getOnlyKline(stockCodeArray,excel=1,start_date='2020-01-01',end_date='2021-12-31'):
    arrayMerage = []
    klineArray = []
    for i in stockCodeArray:
        data_list = []
        code = codeFormat(i)
        rs = bs.query_history_k_data_plus(code,
                                          # 0    1     2    3   4    5      6       7      8        9      10     11          12    13    14    15      16     17
                                          # "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                                          "date,code,open,high,low,close",
                                          start_date= start_date, end_date= end_date,
                                          frequency="d", adjustflag="2")
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        arrayMerage.extend(data_list)
        klineArray.append(data_list) #用在二次处理
    result: DataFrame = pd.DataFrame(arrayMerage)
    result.columns =  ["date","code","open","high","low","close"]
    if excel == 1:
        result.to_excel('/Users/miketam/Downloads/getOnlyKline.xlsx', float_format='%.5f', index=False)
        print(result)
    return klineArray


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
                                          start_date='2020-10-01', end_date='2021-12-31',
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
        maArray = []
        for j in range(0, len(array)): #获取上一个，下一个
            Current = array[j]
            Prev = array[j - 1]
            if Current[6] > 0 and Prev[6] > 0:
                if Current[6] > Prev[6]:
                    ma5 = "向上_5"
                else:
                    ma5 = " "
            if Current[7] > 0 and Prev[7] > 0:
                if Current[7] > Prev[7]:
                    ma10 = "向上_10"
                else:
                    ma10 = " "
            maArrayOneDay = [Current[0], ma5, ma10]



            #这里预留位置，调用函数取"双均线连续3天向下，5日线今天向上"

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
    maMultiStockPd.to_csv("/Users/miketam/Downloads/getMaline.csv", encoding="gbk", index=False)
    maMultiStockPd.to_excel('/Users/miketam/Downloads/getMaline.xlsx', float_format='%.5f', index=False)
    return


