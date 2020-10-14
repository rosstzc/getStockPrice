import datetime

#获取单个股票的各个季度的平均价格，用array保存
from typing import List


def getStockPrice(data):

    # 定义"年季"字典，存储股价平均值
    yearDict = {}
    data = data[::-1]   #股票历史股价列表
    for i in data:
        # DF['DATE'] = pd.to_datetime(DF['DATE']).dt.to_period('Q')
        dateStr = i[0]
        data_time = datetime.datetime.strptime(dateStr, '%Y-%m-%d')  #把字符转换为时间格式
        DATETIME_FORMAT = '%Y'
        yearStr = data_time.strftime(DATETIME_FORMAT)  #把时间格式转换为字符
        quarter = (data_time.month -1) //3 + 1
        yearQuarter = yearStr + "Q" + str(quarter)
        i[0] = yearQuarter
        # print( i[0] + "，" + i[1] +  "，" + i[5])

        #把"年季"写入字典
        yearDict.update({i[0]: ""})
    # print(yearDict)

    # 计算季度平均股价,并填入字典
    for key,value in yearDict.items():
        temp = 0
        k = 0
        for i in data:
            priceClose = float(i[5])
            if key == i[0]:
                temp = temp + priceClose
                k = k + 1
        priceAverage = temp/k
        # print(str(priceAverage))
        yearDict[key] = str(priceAverage)  #给字典填上平均股价
    print(yearDict)

    
    #把各季度股价写入一个数组
    seasonPriceArray: List[str] = []
    for key, value in yearDict.items():
        seasonPriceArray.append(value)
    # print(seasonPriceArray)

    # 以最新股价进行折算
    temp = []
    for i in seasonPriceArray:
        precent = float(i) / float(seasonPriceArray[0])
        temp.append(round(precent,2))
    # print(temp)
    return data,temp




def getAveragePrice(data):

    #提取年份和季度，生成相应字典
    # for i in data:
        # if i[0]

    #计算相应字典的平均值


    #输出年季字典+价格平均值




    return