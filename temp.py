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
                i[0] = dateSeasonFormat(i[0])
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
            data = getSeasonDataOneCode(c) #单个股票，涉及到季度表的数据

            if data[0] != []: #有季表数据
                #循环seasonArray这个数组，逐个季度处理提取数据，如果季度没有数据，就给空值
                k = 0
                for i in seasonArray:
                    if i == data[0][2]:
                        break
                    else:
                        k = k + 1
                for i in data:
                    x = 0
                    while x < k:
                        i.insert(3,'')
                        x = x + 1


                #制作K线PEG、peg股价预测
                season = data[0][2]
                kLinePEGArray = [c, "K线PEG", season]
                pricePEG1Array = [c, "股价(PEG=1）", season]
                pricePEG2Array = [c, "股价(PEG=2)", season]
                pricePEG3Array = [c, "股价(PEG=3）", season]
                x = 0
                while x < k:
                    kLinePEGArray.append('')
                    pricePEG1Array.append('')
                    pricePEG2Array.append('')
                    pricePEG3Array.append('')
                    x = x + 1
                yoyniArray = data[1] #增长率
                epsTTMArray = data[0] #每股收益
                for x in range(3, len(yoyniArray)):
                    if x < len(peArray) :
                        pe = peArray[x]
                    else:
                        print('k线表的pe数据的季度数比季度表的季度数小：'+ str(c))
                        pe = 0
                    g = yoyniArray[x]
                    eps = epsTTMArray[x]
                    if g != '' and pe != '':
                        if g == 0:
                            peg = 0
                        else:
                            peg = round(float(pe/g/100), 2)
                        kLinePEGArray.append(peg)
                        pricePEG1 =  round(float(eps*g*100), 2)
                        pricePEG1Array.append(str(pricePEG1)+"元")
                        pricePEG2Array.append(str(pricePEG1*2)+"元")
                        pricePEG3Array.append(str(float(pricePEG1*3))+"元")


                #制作pb股价预测
                pricePBArray = [c, "股价(净资产*PB）", season]
                pricePBRoeArray  = [c, "股价(净资产(1+ROE)*PB）", season]
                PricePBRoe2Array  = [c, "股价(净资产(1+ROE)2次方*PB）", season]
                #netAsset = eps/roe
                x = 0
                while x < k:
                    pricePBArray.append('')
                    pricePBRoeArray.append('')
                    PricePBRoe2Array.append('')
                    x = x + 1

                for x in range(3, len(epsTTMArray)):
                    if x < len(pbArray): #季度财报比K线日期早，因为上市后回报之前财报也附上
                        pb = pbArray[x]
                        eps = epsTTMArray[x]
                        roe = roeArray[x]
                    else:
                        pb = 0
                        eps = 0
                        roe = 0
                    if eps != '' and pb != '':
                        if roe == 0:
                            pricePB = 0
                            pricePBRoe = 0
                            pricePBRoe2 = 0
                            pricePBArray.append(str(pricePB) + "元")
                            pricePBRoeArray.append(str(pricePBRoe) + "元")
                            PricePBRoe2Array.append(str(pricePBRoe2) + "元")
                        else:
                            pricePB = round(float(eps*pb/roe), 2)
                            pricePBRoe = round(float(eps*pb*(1+roe)/roe), 2)
                            pricePBRoe2 = round(float(eps*pb*(1+roe)*(1+roe)/roe), 2)
                            pricePBArray.append(str(pricePB)+"元")
                            pricePBRoeArray.append(str(pricePBRoe)+"元")
                            PricePBRoe2Array.append(str(pricePBRoe2)+"元")
                        # pricePBRoeArray.append(pricePBRoe)
                        # PricePBRoe2Array.append(pricePBRoe2)


                # return [epsTTMArray, yoyniArray, dupontROEArray, dupontNitogrArray, dupontAssetTurnArray, dupontAssetStoEquityArray]

                stockArray.append(kLinePEGArray)
                stockArray.append(pricePEG1Array)
                stockArray.append(pricePEG2Array)
                stockArray.append(pricePEG3Array)
                stockArray.append(pricePBArray)
                stockArray.append(pricePBRoeArray)
                stockArray.append(PricePBRoe2Array)

            for i in data:
                stockArray.append(i)



    result2 = pd.DataFrame(stockArray)
    result2.to_csv("/Users/miketam/Downloads/getKLineData.csv",encoding="gbk", index=False)
