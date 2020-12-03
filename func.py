import datetime
import pandas as pd
import openpyxl
import numpy as np
from pandas import DataFrame

from multiprocessing import Process


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
            temp2 = maArray[i] * lineNumber - temp + 0.01
        priceForMaUpArray.append(temp2)
    priceForMaUpDf = pd.DataFrame(priceForMaUpArray)
    return priceForMaUpDf

#计算ema线明天向上的最低价格
def getPriceForEmaUp(lineNumber,emaPrevious):
    price = (emaPrevious + 0.01 - emaPrevious*(lineNumber-1)/(lineNumber+1))*(lineNumber+1)/2
    return price

#获取均线向上向下动态
def getTrend(current,previous):
    if current > previous:
        trend = "向上"
    else:
        trend = "向下"
    return trend




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