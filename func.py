import datetime
import pandas as pd
import openpyxl
import numpy as np
import time
import os
from pandas import DataFrame
# from checkPolicy import *
from multiprocessing import Process







#估计bar值所在波形的低、中、高位置, 逐行更新df
def getBarPositionDf(barHLidList,df,i):
    # 估计bar值所在波形的位置
    # 找当前bar到前面bar的H或L点的所有行组成数组，然后找到最近H/L点
    barHLidListTemp = barHLidList[:]  # 复制一份，不修改原始数据
    # 判断i点自己是否是HL点,若是就不用找上一个HL点
    if i == 149:
        tt =1

    if i in barHLidListTemp:
        df.at[i, 'po'] = '低'
        df.at[i, 'bNo'] = 1
    else:
        barHLidListTemp.append(i)
        barHLidListTemp.sort(key=int)
        index2 = barHLidListTemp.index(i)  # index等于0，表明i行前面没有HL点
        if index2 > 0:
            barHLid = barHLidListTemp[index2 - 1]  # 找到该HL点的索引
            dfRow = df.loc[barHLid:i, :]  # HL点到i点的所有行
            barArray = dfRow['bar'].reset_index(drop=True)  # 只取bar值，并且重建索引

            p = getBarPosition(barArray)
            df.at[i, 'po'] = p
            df.at[i, 'bNo'] = len(barArray)
    return df

#判断一个数组的数是不是逐个增大
def biggerThanBefore(Series):
    test = all([Series[i] <= Series[i + 1] for i in range(len(Series) - 1)]) #从知乎找到的牛b方法
    return test

#猜测当前bar值在波形的位置（低、中、高）
def getBarPosition(aSeries):
    #说明：
    # 1）应该切片方式波形的所有值。 另外用numpy来处理数字相关的问题，速度快很多，之前计算哪些rank值时用了循环方式，应该比较费时间
    # 2）用describe的结果来运算

    position = '不确定'
    aSeries = abs(aSeries) #把负值变为正值
    # de = aSeries.describe()
    # count = de['count']
    # mean = de['mean']
    # std = de['std']
    # min = de['min']
    # max = de['max']
    # range75 = de['75%']
    # range50 = de.median()
    # range25 = de['25%']

    count = len(aSeries)
    max = aSeries[aSeries.idxmax()]
    range75 = np.percentile(aSeries, 75)

    # print(aSeries)
    now = aSeries[len(aSeries)-1]
    nowId = aSeries[aSeries.values == now].index[0] #获取元素位置


    #判断位置"低"： 1）bar值当前为最大值，之前所有bar值逐个增大，bar但根数 <= 4
        #判断前面值是否逐个增大

    bigger = biggerThanBefore(aSeries)
    if count <= 2:
        position = '1'
    else:
        if bigger == True and count <= 3:
            position = '1'

        #判断位置"中"
            # 1）之前bar值并非逐个增大，当前bar值属于前1 / 3
            # 2）当前bar值非最大值，上一个是最大值
            # 3）bar值当前为最大值，之前所有bar值逐个增大，bar但根数 > 4
        if bigger == False and now > range75:
            position = '2'
        if now != max and aSeries[nowId-1] == max:
            position = '2'
        if now == max and bigger == True and count >= 4:
            position = '2'

        #判断位置"高"
            # 1）当前bar非最大值，上一个bar值比当前大（但不是最大值）, 当前bar不属于前1 / 3
            # 2）当前bar值和前两个bar值是依次降低
        if bigger != max and  aSeries[nowId-1] > now and aSeries[nowId-1] != max and now < range75:
            position = '3'

        if nowId > 1 and aSeries[nowId-2] > aSeries[nowId-1] and aSeries[nowId-1] > now:
            position = '3'
    return position

#计算Kdj
def getDfKdj(kLineDf):
    # 计算kdj
    low_list = kLineDf[4].rolling(9, min_periods=9).min()
    low_list.fillna(value=kLineDf[4].expanding().min(), inplace=True)
    high_list = kLineDf[3].rolling(9, min_periods=9).max()
    high_list.fillna(value=kLineDf[3].expanding().max(), inplace=True)
    rsv = (kLineDf[5] - low_list) / (high_list - low_list) * 100

    kLineDf['k'] = pd.DataFrame(rsv).ewm(com=2).mean()
    kLineDf['d'] = kLineDf['k'].ewm(com=2).mean()
    kLineDf['j'] = 3 * kLineDf['k'] - 2 * kLineDf['d']

    #k是否向上，比上一值大
    kLineDf['kTrend'] = np.where(kLineDf['k'] > kLineDf['k'].shift(+1),"k向上","")
    kLineDf['jTrend'] = np.where(kLineDf['j'] > kLineDf['j'].shift(+1),"j向上","")
    #k值是否大于30少于50
    kLineDf['k50'] = np.where(kLineDf['k'] <= 25,"k少于25","")
    kLineDf['k50'] = np.where((kLineDf['k'] > 25) & (kLineDf['k'] <= 50),"k少于50",kLineDf['k50'])
    # kLineDf['k50'] = np.where( (kLineDf['k'] > 50) & (kLineDf['kTrend']=='k向上'),"k穿过50",kLineDf['k50'])
    kLineDf['k50'] = np.where((kLineDf['k'].shift(+1) < 50) & (kLineDf['k'] > 50) & (kLineDf['kTrend']=='k向上'),"k穿过50", kLineDf['k50'])

    #j值少于20并向上
    kLineDf['j20'] = np.where((kLineDf['j'] < 20) & (kLineDf['jTrend']=='j向上'),"j向上少于20", '')
    #j值上穿20
    kLineDf['j20'] = np.where((kLineDf['j'].shift(+1) < 20) & (kLineDf['j'] > 20) & (kLineDf['jTrend']=='j向上'),"j穿过20", kLineDf['j20'])


    return kLineDf


def outPutXlsx(df):
    df.to_excel('/Users/miketam/Downloads/temp.xlsx', float_format='%.5f',index=False)


#在df计算macd
def getDfMacd(df2):
    # #MACD相关
    df = df2[[5]]
    df.reset_index(level=0, inplace=True)
    df.columns = ['ds', 'y']
    exp1 = df.y.ewm(span=12, adjust=False).mean()
    exp2 = df.y.ewm(span=26, adjust=False).mean()
    # exp3 = df.y.ewm(span=9, adjust=False).mean()
    df2['ema12'] = exp1
    df2['ema26'] = exp2

    dif = exp1 - exp2
    deaa = dif.ewm(span=9, adjust=False).mean()
    bar = (dif - deaa) * 2
    df2['dif'] = dif  # 快
    df2['dea'] = deaa  # 慢
    df2['bar'] = bar  # 柱状

    df = df2
    # 计算dea的HL点
    df['deaHL'] = np.where((df['dea'] - df['dea'].shift(1) >= 0) & (df['dea'] - df['dea'].shift(-1) >= 0), 'H',
                           df['dea'])
    df['deaHL'] = np.where((df['dea'] - df['dea'].shift(1) <= 0) & (df['dea'] - df['dea'].shift(-1) <= 0), 'L',
                           df['deaHL'])
    df['barHL'] = np.where((df['bar'].shift(1) > 0) & (df['bar'] < 0), 'H', '')
    df['barHL'] = np.where((df['bar'].shift(1) < 0) & (df['bar'] > 0), 'L', df['barHL'])

    # 计算bar的HL点
    df['barHL'] = np.where((df['bar'].shift(1) > 0) & (df['bar'] < 0), 'H', '')
    df['barHL'] = np.where((df['bar'].shift(1) < 0) & (df['bar'] > 0), 'L', df['barHL'])
    df['bTrend'] = np.where((df['bar'] > 0), '向上', ' ')

    # 计算bar值对比前一日是增加还是减少，用0/1, -1/-0 来表示
    df['barKey'] = np.where((df['bar'].shift(1) > 0) & (df['bar'] > 0) & (df['bar'] > df['bar'].shift(1)), '1', '')
    df['barKey'] = np.where((df['bar'].shift(1) > 0) & (df['bar'] > 0) & (df['bar'] < df['bar'].shift(1)), '0',df['barKey'])
    df['barKey'] = np.where((df['bar'].shift(1) < 0) & (df['bar'] > 0), '1',df['barKey'])

    df['barKey'] = np.where((df['bar'].shift(1) < 0) & (df['bar'] < 0) & (df['bar'] > df['bar'].shift(1)), '-1',df['barKey'])
    df['barKey'] = np.where((df['bar'].shift(1) < 0) & (df['bar'] < 0) & (df['bar'] < df['bar'].shift(1)), '-0',df['barKey'])
    df['barKey'] = np.where((df['bar'].shift(1) > 0) & (df['bar'] < 0), '0', df['barKey'])

    return df2

#把日期字符串转化为年份周，如2018-2， 表示2018年第二周
def getYearWeekFromDate(dateStr):
    date_time = datetime.datetime.strptime(dateStr, '%Y-%m-%d')
    calendar = date_time.isocalendar()  # 得到[年，第几周，周几]
    yearWeek = str(calendar[0]) + '_' + str(calendar[1])
    return yearWeek

# 按股票代码拆分df
def dfDivide(stockCodeArray, df):
    codeArray = []
    dfArray = []
    for i in stockCodeArray:
        code = codeFormat(i)
        codeArray.append(code)

    # 按股票拆分df
    for i in codeArray:
        data = df.loc[(df['code'] == i)].copy()
        data = data.reset_index(drop=True)
        dfArray.append(data)
    return dfArray

def moving_average_convergence(group, nslow=26, nfast=12):
    emaslow = pd.ewma(group, span=nslow, min_periods=1)
    emafast = pd.ewma(group, span=nfast, min_periods=1)
    result = pd.DataFrame({'MACD': emafast-emaslow, 'emaSlw': emaslow, 'emaFst': emafast})
    return result



#计算ma线明天最低向上价格
def getPriceForMaUp(lineNumber, closePriceArray, maArray):
    # 计算最低向上价格。把df列变为数组，在数组运算后再变为df
    priceForMaUpArray = [0]
    for i in range(len(closePriceArray)):
        temp = 0
        temp2 = 0
        number =lineNumber - 1
        if i >= number:
            for j in range(number):
                temp = temp + float(closePriceArray[i - j])
            temp2 = maArray[i] * lineNumber - temp + 0.001
        priceForMaUpArray.append(temp2)
    priceForMaUpDf = pd.DataFrame(priceForMaUpArray)
    return priceForMaUpDf

#计算ema线明天向上的最低价格
def getPriceForEmaUp(lineNumber,emaPrevious):
    price = (emaPrevious + 0.001 - emaPrevious*(lineNumber-1)/(lineNumber+1))*(lineNumber+1)/2
    return price

#获取均线向上向下动态
def getTrend(current,previous):
    if current > previous:
        trend = "向上"
    else:
        trend = "向下"
    return trend


#把百分数字符转化为数字
def str2Float(string):
    string = string.strip("%")
    floatStr = abs(float(string) / 100)
    return floatStr

def codeFormat(code) -> object:
    temp = code[0:1]
    if temp == '3' or temp == '0':
        # print("深交所代码")
        code = "sz." + code
    else:
        code = "sh." + code
    #print(code)
    return code


def dateSeasonFormat(date):
    dateStr = date
    data_time = datetime.datetime.strptime(dateStr, '%Y-%m-%d')  # 把字符转换为时间格式
    DATETIME_FORMAT = '%Y'
    yearStr = data_time.strftime(DATETIME_FORMAT)  # 把时间格式转换为字符
    quarter = (data_time.month - 1) // 3 + 1
    yearQuarter = yearStr + "Q" + str(quarter)
    date = yearQuarter  # 修改日期为 XXXX年XX季度
    # print( i[0] + "，" + i[1] +  "，" + i["close"])
    return date



def func1(args):
    print('测试%s多进程' %args)

def multiProcess():
    process_list = []
    # for i in range(1):
    p = Process(target=func1, args=('test',))
    p.start()
    p.join()
    # process_list.append(p)
    # for i in process_list:
    #     p.join()
    print("test finish")