import baostock as bs
import pandas as pd
import openpyxl
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
from func import *





def checkPolicy(stockCodeArray):
    dfArray = processKline(stockCodeArray)
    for i in stockCodeArray:

        return



#K线数据二次加工
def processKline(stockCodeArray):
    kLineArray = getOnlyKline(stockCodeArray,0)
    dfAppend:DataFrame = pd.DataFrame()
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

        #均线动态(收盘价)
        kLineDf["ma5Trend"] = np.where( kLineDf['ma5'] > kLineDf['ma5'].shift(+1) ,"向上","")
        kLineDf["ma10Trend"] = np.where( kLineDf['ma10'] > kLineDf['ma10'].shift(+1) ,"向上","")

        #5日线，10日线是否双向上
        kLineDf["ma5ma10Trend"] = np.where((kLineDf["ma5Trend"]=="向上") & (kLineDf["ma10Trend"]=="向上"),"是","")

        new = ['用双向上基线做的预测值']  #新增一行，方便显示均线向上的最低值。一定要价true这个参数
        kLineDf = kLineDf.append(new,ignore_index=True)

        # 计算最低向上价格。把df列变为数组，在数组运算后再变为df
        closePriceArray = kLineDf[5].values
        ma5Array = kLineDf["ma5"].values
        ma10Array = kLineDf["ma10"].values
        kLineDf["priceForMa5Up"] = getPriceForMaUp(5,closePriceArray,ma5Array)
        kLineDf["priceForMa10Up"] = getPriceForMaUp(10,closePriceArray,ma10Array)
        kLineDf["priceForMa5Ma10Up"] = np.where(kLineDf["priceForMa5Up"] > kLineDf["priceForMa10Up"],kLineDf["priceForMa5Up"],kLineDf["priceForMa10Up"])#双向上最低价

        kLineDf[2] = pd.to_numeric(kLineDf[2]) #开盘价，把字符转化为数字
        kLineDf[3] = pd.to_numeric(kLineDf[3]) #最高价，把字符转化为数字
        kLineDf[4] = pd.to_numeric(kLineDf[4]) #最低价，把字符转化为数字
        kLineDf[5] = pd.to_numeric(kLineDf[5]) #收盘价，把字符转化为数字

        # #给双向上指标增加动态
        kLineDf["ma5ma10Trend"] = np.where((kLineDf["ma5ma10Trend"] == '是')&(kLineDf[4] < kLineDf["priceForMa5Ma10Up"]),'是，有向下', kLineDf["ma5ma10Trend"])
        kLineDf["ma5ma10Trend"] = np.where((kLineDf["ma5ma10Trend"] == '')&(kLineDf[3] > kLineDf["priceForMa5Ma10Up"]),'有双向上', kLineDf["ma5ma10Trend"])

        #双向上价是否在K线内
        kLineDf["priceForMa5Ma10UpInKLine"] = np.where((kLineDf[4] < kLineDf["priceForMa5Ma10Up"])&(kLineDf["priceForMa5Ma10Up"] < kLineDf[3]),'Y','')

        #把双向上基线放放到收盘价作为参考，并更新ma5、ma10作为参考
        index = len(kLineDf)-1
        kLineDf.at[index,5] = kLineDf.at[index, 'priceForMa5Ma10Up']
        kLineDf["ma5"] = kLineDf[5].rolling(window=5).mean() #再次更新一下均线
        kLineDf["ma10"] = kLineDf[5].rolling(window=10).mean()  #再次更新一下均线
        kLineDf.at[index, 1] = x[0][1]

        #双向上基线对比10日线
        kLineDf["priceForMa5Ma10UpVsMa10"] = kLineDf["priceForMa5Ma10Up"] / kLineDf["ma10"] - 1
        kLineDf["priceForMa5Ma10UpVsMa10"] = kLineDf["priceForMa5Ma10UpVsMa10"].apply(lambda x: format(x, '.2%'))

        ##双向上价/收盘价
        kLineDf["priceForMa5Ma10UpVsClosePrice"] = kLineDf["priceForMa5Ma10Up"] / kLineDf[5] - 1
        kLineDf["priceForMa5Ma10UpVsClosePrice"] = kLineDf["priceForMa5Ma10UpVsClosePrice"].apply(lambda x: format(x, '.2%'))

        # kLineDf["priceForMa5Ma10UpVsLowPrice"] #最低价/双向上价
        kLineDf["lowPriceVsPriceForMa5Ma10Up"] = kLineDf[4] / kLineDf["priceForMa5Ma10Up"] - 1
        kLineDf["lowPriceVsPriceForMa5Ma10Up"] = kLineDf["lowPriceVsPriceForMa5Ma10Up"].apply(lambda x: format(x, '.2%'))

        # kLineDf["priceForMa5Ma10UpVsHighPrice"] #最高价/双向上价
        kLineDf["highPriceVsPriceForMa5Ma10Up"] = kLineDf[3]/ kLineDf["priceForMa5Ma10Up"] - 1
        kLineDf["highPriceVsPriceForMa5Ma10Up"] = kLineDf["highPriceVsPriceForMa5Ma10Up"].apply(lambda x: format(x, '.2%'))

        # #MACD相关
        # kLineDf["macd12"]
        # kLineDf["macd26"]
        # kLineDf["macdQuick"]
        # kLineDf["macdSlow"]
        df = kLineDf[[5]]
        df.reset_index(level=0, inplace=True)
        df.columns = ['ds', 'y']
        exp1 = df.y.ewm(span=12, adjust=False).mean()
        exp2 = df.y.ewm(span=26, adjust=False).mean()
        exp3 = df.y.ewm(span=9, adjust=False).mean()

        dif = exp1 - exp2
        deaa = dif.ewm(span=9, adjust=False).mean()
        macd = (dif - deaa)*2
        kLineDf['macd_dif'] = dif #快
        kLineDf['macd_dea'] = deaa #慢
        kLineDf['macd_macd'] = macd #柱状

        ##制作图macd
        # plt.plot(df.ds, dif, label='dif',color='orange')
        # plt.plot(df.ds, deaa, label='dea', )
        # # plt.plot(df.ds, macd, label='macd', color='Magenta')
        # plt.legend(loc='upper left')
        # plt.show()

########下面开始计算ema的数据##########
        kLineDf['closeEma'] = kLineDf[5]  #为方便ema双向上的预测收盘价，新增一列收盘价

        kLineDf['ema12'] = exp1
        kLineDf['ema26'] = exp2

        kLineDf["ema12VsEma26"] = np.where(kLineDf['ema12'] > kLineDf['ema26'] ,"大于","") #两均线比较

        #均线动态(收盘价)
        kLineDf["ema12Trend"] = np.where( kLineDf['ema12'] > kLineDf['ema12'].shift(+1) ,"向上","")
        kLineDf["ema26Trend"] = np.where( kLineDf['ema26'] > kLineDf['ema26'].shift(+1) ,"向上","")

        #5日线，10日线是否双向上
        kLineDf["ema12ema26Trend"] = np.where((kLineDf["ema12Trend"]=="向上") & (kLineDf["ema26Trend"]=="向上"),"是","")

        #计算ema线向上的最低价格
        kLineDf["priceForEma12Up"] = getPriceForEmaUp(12,kLineDf['ema12'].shift(+1)) #当前行计算是下一日的最低向上价格
        kLineDf["priceForEma26Up"] = getPriceForEmaUp(26,kLineDf['ema26'].shift(+1))
        kLineDf["priceForEma12Ema26Up"] = np.where(kLineDf["priceForEma12Up"] > kLineDf["priceForEma26Up"],kLineDf["priceForEma12Up"],kLineDf["priceForEma26Up"])

        #更新最后一个收盘价(EMA)作为预测，然后在更新ema均线，同时也更新两个ema线
        kLineDf.at[index,'closeEma'] = kLineDf.at[index, 'priceForEma12Ema26Up']
        kLineDf['ema12'] = kLineDf['ema12'].ewm(span=12, adjust=False).mean()
        kLineDf['ema26'] = kLineDf['ema26'].ewm(span=26, adjust=False).mean()

        # #给ema双向上指标增加动态
        kLineDf["ema12ema26Trend"] = np.where((kLineDf["ema12ema26Trend"] == '是')&(kLineDf[4] < kLineDf["priceForEma12Ema26Up"]),'是，有向下', kLineDf["ema12ema26Trend"])
        kLineDf["ema12ema26Trend"] = np.where((kLineDf["ema12ema26Trend"] == '')&(kLineDf[3] > kLineDf["priceForEma12Ema26Up"]),'有双向上', kLineDf["ema12ema26Trend"])

        #双向上价是否在K线内
        kLineDf["priceForEma12Ema26UpInKLine"] = np.where((kLineDf[4] < kLineDf["priceForEma12Ema26Up"])&(kLineDf["priceForEma12Ema26Up"] < kLineDf[3]),'Y','')

        # ema双向上基线对比ema26日线
        kLineDf["priceForEma12Ema26UpVsEma26"] = kLineDf["priceForEma12Ema26Up"] / kLineDf["ema26"] - 1
        kLineDf["priceForEma12Ema26UpVsEma26"] = kLineDf["priceForEma12Ema26UpVsEma26"].apply(lambda x: format(x, '.2%'))

        ##ema双向上价/收盘价
        kLineDf["priceForEma12Ema26UpVsClosePrice"] = kLineDf["priceForEma12Ema26Up"] / kLineDf[5] - 1
        kLineDf["priceForEma12Ema26UpVsClosePrice"] = kLineDf["priceForEma12Ema26UpVsClosePrice"].apply(lambda x: format(x, '.2%'))

         #最低价/ema双向上价
        kLineDf["lowPriceVspriceForEma12Ema26Up"] = kLineDf[4] / kLineDf["priceForEma12Ema26Up"] - 1
        kLineDf["lowPriceVspriceForEma12Ema26Up"] = kLineDf["lowPriceVspriceForEma12Ema26Up"].apply(lambda x: format(x, '.2%'))

         #最高价/ema双向上价
        kLineDf["highPriceVspriceForEma12Ema26Up"] = kLineDf[3] / kLineDf["priceForEma12Ema26Up"] - 1
        kLineDf["highPriceVspriceForEma12Ema26Up"] = kLineDf["highPriceVspriceForEma12Ema26Up"].apply(lambda x: format(x, '.2%'))


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

        dfAppend = dfAppend.append(kLineDf)
        ### 结果集输出到csv文件 ####
    dfAppend.to_csv("/Users/miketam/Downloads/processKline.csv", encoding="gbk", index=False)
    # macd.to_csv("/Users/miketam/Downloads/processKline_macd.csv", encoding="gbk", index=False)
    print(dfAppend)

    dfAppend.to_excel('/Users/miketam/Downloads/processKline.xlsx', float_format='%.5f',index=False)
    return dfAppend


#获取最基础到K线数据
def getOnlyKline(stockCodeArray,excel=1,start_date='2020-01-01',end_date='2023-10-31'):
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
    maMultiStockPd.to_csv("/Users/miketam/Downloads/getMaline.csv", encoding="gbk", index=False)
    maMultiStockPd.to_excel('/Users/miketam/Downloads/getMaline.xlsx', float_format='%.5f', index=False)
    return


