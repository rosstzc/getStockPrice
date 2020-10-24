# 处理股票平均季度股价
def getStockPrice(data):
    # 定义"年季"字典，存储股价平均值
    yearDict = {}
    data = data[::-1]  # 股票历史股价列表，设置排序为时间从近到远
    for i in data:
        # DF['DATE'] = pd.to_datetime(DF['DATE']).dt.to_period('Q')
        dateStr = i[0]
        data_time = datetime.datetime.strptime(dateStr, '%Y-%m-%d')  # 把字符转换为时间格式
        DATETIME_FORMAT = '%Y'
        yearStr = data_time.strftime(DATETIME_FORMAT)  # 把时间格式转换为字符
        quarter = (data_time.month - 1) // 3 + 1
        yearQuarter = yearStr + "Q" + str(quarter)
        i[0] = yearQuarter  # 修改日期为 XXXX年XX季度
        # print( i[0] + "，" + i[1] +  "，" + i[5])

        # 把"年季"写入字典
        yearDict.update({i[0]: ""})
    # print(yearDict)

    # 计算季度平均股价,并填入字典； 增加计算PE、PB统计
    peArray = []
    pbArray = []
    for key, value in yearDict.items():
        temp = 0
        k = 0
        for i in data:
            priceClose = float(i[5])
            if key == i[0]:
                temp = temp + priceClose
                k = k + 1
                # 增加PE、PB统计

        priceAverage = temp / k
        # print(str(priceAverage))
        yearDict[key] = str(priceAverage)  # 给字典填上季度平均股价
    print(yearDict)

    # 把各季度股价写入一个数组
    seasonPriceArray: List[str] = []
    for key, value in yearDict.items():
        seasonPriceArray.append(value)
    # print(seasonPriceArray)

    # 以最新股价进行折算
    temp = [round(float(seasonPriceArray[0]), 2)] #先写入最新价格，之后再把所有价格与最新价进行折算
    for i in seasonPriceArray:
        precent = float(i) / float(seasonPriceArray[0])
        temp.append(round(precent, 2))
    # print(temp)
    return data, temp