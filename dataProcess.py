import datetime
import baostock as bs
import pandas as pd

#获取单个股票的各个季度的平均价格，用array保存
from typing import List


#处理股票平均季度股价
# def getStockPrice(data):
#
#     # 定义"年季"字典，存储股价平均值
#     yearDict = {}
#     data = data[::-1]   #股票历史股价列表，设置排序为时间从近到远
#     for i in data:
#         # DF['DATE'] = pd.to_datetime(DF['DATE']).dt.to_period('Q')
#         dateStr = i[0]
#         data_time = datetime.datetime.strptime(dateStr, '%Y-%m-%d')  #把字符转换为时间格式
#         DATETIME_FORMAT = '%Y'
#         yearStr = data_time.strftime(DATETIME_FORMAT)  #把时间格式转换为字符
#         quarter = (data_time.month -1) //3 + 1
#         yearQuarter = yearStr + "Q" + str(quarter)
#         i[0] = yearQuarter #修改日期为 XXXX年XX季度
#         # print( i[0] + "，" + i[1] +  "，" + i[5])
#
#         #把"年季"写入字典
#         yearDict.update({i[0]: ""})
#     # print(yearDict)
#
#     # 计算季度平均股价,并填入字典； 增加计算PE、PB统计
#     peArray = []
#     pbArray = []
#     for key,value in yearDict.items():
#         temp = 0
#         k = 0
#         for i in data:
#             priceClose = float(i[5])
#             if key == i[0]:
#                 temp = temp + priceClose
#                 k = k + 1
#                 #增加PE、PB统计
#
#         priceAverage = temp/k
#         # print(str(priceAverage))
#         yearDict[key] = str(priceAverage)  #给字典填上季度平均股价
#     print(yearDict)
#
#
#     #把各季度股价写入一个数组
#     seasonPriceArray: List[str] = []
#     for key, value in yearDict.items():
#         seasonPriceArray.append(value)
#     # print(seasonPriceArray)
#
#     # 以最新股价进行折算
#     temp = [round(float(seasonPriceArray[0]),2)]
#     for i in seasonPriceArray:
#         precent = float(i) / float(seasonPriceArray[0])
#         temp.append(round(precent,2))
#     # print(temp)
#     return data,temp


def getSeasonDataOneCode(i,array):
    profit_list = []
    growth_list = []
    dupont_list = []
    code = codeFormat(i)
    for j in range(2015, 2023):
        for k in range(1, 5):
            # 读取季度盈利
            rs_profit = bs.query_profit_data(code=code, year=j, quarter=k)
            while (rs_profit.error_code == '0') & rs_profit.next():
                profit_list.append(rs_profit.get_row_data())

            # 读取季度成长
            rs_growth = bs.query_growth_data(code=code, year=j, quarter=k)
            while (rs_growth.error_code == '0') & rs_growth.next():
                growth_list.append(rs_growth.get_row_data())

            # 读取杜邦分析
            rs_dupont = bs.query_dupont_data(code=code, year=j, quarter=k)
            while (rs_dupont.error_code == '0') & rs_dupont.next():
                dupont_list.append(rs_dupont.get_row_data())

    # 处理盈利分析
    profit_list = profit_list[::-1]
    epsTTMArray = [i, "每股收益/epsTTM", profit_list[0][2]]  # 每股收益
    # roeAvgArray = [i, "净资产收益率/roeAvg",profit_list[0][2]] #净资产收益率
    for x in profit_list:
        epsTTMArray.append(round(float(x[7]), 2))
        # roeAvgArray.append(round(float(x[3]),2))

    # 处理成长
    growth_list = growth_list[::-1]
    yoyniArray = [i, "净利润同比增长率G/yoyni", growth_list[0][2]]  # 净利润同比增长率
    for x in growth_list:
        yoyniArray.append(round(float(x[5]), 2))

    # 处理杜邦分析
    dupont_list = dupont_list[::-1]
    dupontROEArray = [i, "净资产收益率/dupontROE", dupont_list[0][2]]  # 杜邦表ROE，净资产收益率
    dupontNitogrArray = [i, "销售净利润率/dupontNitogr", dupont_list[0][2]]  # 销售净利润率，净利润/营业总收入
    dupontAssetTurnArray = [i, "总资产周转率/dupontAssetTurn", dupont_list[0][2]]  # 总资产周转率
    dupontAssetStoEquityArray = [i, "权益乘数/dupontAssetStoEquity", dupont_list[0][2]]  # 权益乘数

    for x in dupont_list:
        dupontROEArray.append(round(float(x[3]), 3))
        dupontNitogrArray.append(round(float(x[7]), 2))
        if x[5] == '':
            dupontAssetTurnArray.append('')
        else:
            dupontAssetTurnArray.append(round(float(x[5]), 2))
        dupontAssetStoEquityArray.append(round(float(x[4]), 2))

    # 把数据聚合
    array.append(epsTTMArray)
    # array.append(roeAvgArray)
    array.append(yoyniArray)

    array.append(dupontROEArray)
    array.append(dupontNitogrArray)
    array.append(dupontAssetTurnArray)
    array.append(dupontAssetStoEquityArray)

    return array

#获取季度到各种数据
def getSeasonData(stockCodeArray):
    array = []
    for i in stockCodeArray:
        array = getSeasonDataOneCode(i,array)
    result_profit = pd.DataFrame(array)
    result_profit.to_csv("/Users/miketam/Downloads/getSeasonData.csv", encoding="gbk", index=False)

# def getSeasonDataBak(stockCodeArray):
#     array = []
#     for i in stockCodeArray:
#         profit_list = []
#         growth_list = []
#         dupont_list = []
#
#         code = codeFormat(i)
#         for j in range(2015, 2023):
#             for k in range(1, 5):
#                 #读取季度盈利
#                 rs_profit = bs.query_profit_data(code=code, year=j, quarter=k)
#                 while (rs_profit.error_code == '0') & rs_profit.next():
#                     profit_list.append(rs_profit.get_row_data())
#
#                 #读取季度成长
#                 rs_growth = bs.query_growth_data(code=code, year=j, quarter=k)
#                 while (rs_growth.error_code == '0') & rs_growth.next():
#                     growth_list.append(rs_growth.get_row_data())
#
#                 #读取杜邦分析
#                 rs_dupont = bs.query_dupont_data(code=code, year=j, quarter=k)
#                 while (rs_dupont.error_code == '0') & rs_dupont.next():
#                     dupont_list.append(rs_dupont.get_row_data())
#
#         #处理盈利分析
#         profit_list = profit_list[::-1]
#         epsTTMArray = [i, "每股收益/epsTTM",profit_list[0][2]]  #每股收益
#         # roeAvgArray = [i, "净资产收益率/roeAvg",profit_list[0][2]] #净资产收益率
#         for x in profit_list:
#             epsTTMArray.append(round(float(x[7]),2))
#             # roeAvgArray.append(round(float(x[3]),2))
#
#         #处理成长
#         growth_list = growth_list[::-1]
#         yoyniArray = [i, "净利润同比增长率G/yoyni",growth_list[0][2]] #净利润同比增长率
#         for x in growth_list:
#             yoyniArray.append(round(float(x[5]),2))
#
#         #处理杜邦分析
#         dupont_list = dupont_list[::-1]
#         dupontROEArray = [i, "净资产收益率/dupontROE",dupont_list[0][2]] #杜邦表ROE，净资产收益率
#         dupontNitogrArray = [i, "销售净利润率/dupontNitogr",dupont_list[0][2]] #销售净利润率，净利润/营业总收入
#         dupontAssetTurnArray = [i, "总资产周转率/dupontAssetTurn",dupont_list[0][2]] #总资产周转率
#         dupontAssetStoEquityArray = [i, "权益乘数/dupontAssetStoEquity",dupont_list[0][2]] #权益乘数
#
#         for x in dupont_list:
#             dupontROEArray.append(round(float(x[3]),3))
#             dupontNitogrArray.append(round(float(x[7]),2))
#             if x[5] == '':
#                 dupontAssetTurnArray.append('')
#             else:
#                 dupontAssetTurnArray.append(round(float(x[5]),2))
#             dupontAssetStoEquityArray.append(round(float(x[4]),2))
#
#         #把数据聚合
#         array.append(epsTTMArray)
#         # array.append(roeAvgArray)
#         array.append(yoyniArray)
#
#         array.append(dupontROEArray)
#         array.append(dupontNitogrArray)
#         array.append(dupontAssetTurnArray)
#         array.append(dupontAssetStoEquityArray)
#
#     result_profit = pd.DataFrame(array)
#     result_profit.to_csv("/Users/miketam/Downloads/getSeasonData.csv", encoding="gbk", index=False)


#获取K线数据
def getKlineData(stockCodeArray):
    stockArray = []
    for c in stockCodeArray:
        code = codeFormat(c)
        rs = bs.query_history_k_data_plus(code,
                                          # 0    1     2    3   4    5      6       7      8        9      10     11          12    13    14    15      16     17
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                                          start_date='2015-01-01', end_date='2021-12-31',
                                          frequency="d", adjustflag="2")
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())

        seasonArray = []  # 季度数组
        data_list = data_list[::-1]  # 股票历史股价列表，设置排序为时间从近到远
        for i in data_list:
            dateStr = i[0]
            data_time = datetime.datetime.strptime(dateStr, '%Y-%m-%d')  # 把字符转换为时间格式
            DATETIME_FORMAT = '%Y'
            yearStr = data_time.strftime(DATETIME_FORMAT)  # 把时间格式转换为字符
            quarter = (data_time.month - 1) // 3 + 1
            yearQuarter = yearStr + "Q" + str(quarter)
            i[0] = yearQuarter  # 修改日期为 XXXX年XX季度
            # print( i[0] + "，" + i[1] +  "，" + i[5])

            # 把"年季"写入数组
            if i[0] not in seasonArray:
                seasonArray.append(i[0])

        priceArray = [] #平均股价数组
        peArray = []
        pbArray = []
        roeArray = []
        for j in seasonArray:
            tempPrice = 0
            tempPE = 0
            tempPB = 0
            tempROE = 0
            k = 0
            for i in data_list:
                if j == i[0]:
                    tempPrice = tempPrice + float(i[5]) #股价
                    tempPE = tempPE + float(i[13])  #pe
                    tempPB = tempPB + float(i[14])  #pb
                    tempROE = tempROE + float(i[14])/float(i[13]) #pb

                    k = k + 1
            priceAvg = tempPrice / k
            peAvg = tempPE / k
            pbAvg = tempPB / k
            roeAvg = tempROE / k
            if priceArray == []:
                priceArray.append(round(priceAvg, 2)) #最近季度平均股价
            else:
                priceArray.append(round(priceAvg/float(priceArray[0]), 2)) #把过去季度股价与最近季度股价折算
            peArray.append(round(peAvg,2) )
            pbArray.append(round(pbAvg,2) )
            roeArray.append(round(roeAvg,3))

        # stockPriceAverage = getStockPrice(data_list)[1]  # 生成季度平均股价，单个股票
        priceArray.insert(0, seasonArray[0])
        priceArray.insert(0, "股价/前复权+折算")  #
        priceArray.insert(0, c)  # 在数组前面插入股票代码

        peArray.insert(0, seasonArray[0])
        peArray.insert(0, "滚动PE/peTTM")  #
        peArray.insert(0, c)

        pbArray.insert(0, seasonArray[0])
        pbArray.insert(0, "滚动市净率/pbMRQ")  #
        pbArray.insert(0, c)

        roeArray.insert(0, seasonArray[0])
        roeArray.insert(0, "K线ROE/roeKline")  #
        roeArray.insert(0, c)

        stockArray.append(priceArray)
        stockArray.append(peArray)
        stockArray.append(pbArray)
        stockArray.append(roeArray)

        #把与季度接口相关数据放在这里处理

        stockArray = getSeasonDataOneCode(c,stockArray) #单个股票，涉及到季度表的数据

        #流程： 1 季度数据的季度时间转化为2020Q1这个格式  2 循环seasonArray这个数组，逐个季度处理提取数据，如果季度没有数据，就给空值







    result2 = pd.DataFrame(stockArray)
    result2.to_csv("/Users/miketam/Downloads/getKLineData.csv",encoding="gbk", index=False)



#获取 epsTTM每股受益/盈利接口
# def getEpsTTM(code):
#     epsTTMArray = [code,"epsTTM"] #这里添加是原始股票代码
#     code = codeFormat(code) #API要加sz、sh后到股票代码
#     profit_list = []
#     for i in range(2015,2023):
#         for j in range(1,5):
#             rs_profit = bs.query_profit_data(code=code, year=i, quarter=j)
#             while (rs_profit.error_code == '0') & rs_profit.next():
#                 profit_list.append(rs_profit.get_row_data())
#                 # print(str(i) + "年" + str(j) + "季有数据")
#             # epsTTM= profit_list[0][7]
#             # epsTTMArray.append(epsTTM)
#
#             result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)
#             # 打印输出
#             # print(result_profit)
#             # 结果集输出到csv文件
#             result_profit.to_csv("/Users/miketam/Downloads/getEpsTTM.csv", encoding="gbk", index=False)
#     #把多个季度合并为一行
#     profit_list = profit_list[::-1]
#     epsTTMArray.append("最近季度：" + profit_list[0][2])
#     for i in profit_list:
#         epsTTMArray.append(i[7])
#         # print(i[7])
#     result_profit = pd.DataFrame(epsTTMArray)
#     result_profit.to_csv("/Users/miketam/Downloads/getEpsTTMArray.csv", encoding="gbk", index=False)

def codeFormat(code):
    temp = code[0:1]
    if temp == '3' or temp == '0':
        # print("深交所代码")
        code = "sz." + code
    else:
        code = "sh." + code
    #print(code)
    return code

def getAveragePrice(data):

    #提取年份和季度，生成相应字典
    # for i in data:
        # if i[0]

    #计算相应字典的平均值


    #输出年季字典+价格平均值




    return