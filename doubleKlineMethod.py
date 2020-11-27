import baostock as bs
import pandas as pd
import openpyxl
import numpy as np
from pandas import DataFrame

from func import *


def getOnlyKline(stockCodeArray):
    array = []
    for i in stockCodeArray:
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
        array.extend(data_list)

    result: DataFrame = pd.DataFrame(array)
    ### 结果集输出到csv文件 ####
    result.to_csv("/Users/miketam/Downloads/getOnlyKline.csv", encoding="gbk", index=False)
    print(result)

    result.to_excel('/Users/miketam/Downloads/getOnlyKline.xlsx', float_format='%.5f',index=False)
    # writer = pd.ExcelWriter('/Users/miketam/Downloads/getMaline.xlsx')
    # result.to_excel(writer, float_format='%.5f')
    # writer.save()


#获取均线方法
def getMaLine(stockCodeArray,stockNameArray):
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
        array = result.values
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


