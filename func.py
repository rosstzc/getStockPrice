import datetime
import pandas as pd
import openpyxl
import numpy as np
import time
import os
from pandas import DataFrame
import mplfinance as mpf
# from checkPolicy import *
from multiprocessing import Process





#周期内背离
    #算法说明：1）底背离：从最后一个柱子往前找到-0转-1的所有点， 从后向前比较，

#周期外背离

def getChartTest(df, filePath, type=''):
    code = df.iat[1,1]#股票代码
    df.drop(index=len(df) - 1, inplace=True)
    df = df.tail(200)
    df['date'] = pd.to_datetime(df['date']) #
    df.set_index('date', inplace=True)

    if type == 'day':
        # ema21_WList = df['ema21_W'].tolist()
        # ema21_WList2 =  list(set(ema21_WList)) #去重复
        # ema21_WList2.sort(key=ema21_WList.index)  #按原来排序
        # temp = []
        # for i in range(len(ema21_WList2)):
        #     if ema21_WList2[i] > ema21_WList2[i+1] and  ema21_WList2[i+1] < ema21_WList2[i+2] and i+2 < len(ema21_WList2): #找到向下转向上
        #         temp.append(ema21_WList2[i+1])

        #找到ema由向下转向上的第二周
        df2 = df.drop_duplicates(subset=['date_W'], keep='last', ignore_index=True)  # 只保留每周最后一条记录
        a = df2['ema21_W'].shift(3)
        b = df2['ema21_W'].shift(2)
        c = df2['ema21_W'].shift(1) #由向下转向上
        d = df2['ema21_W'] #之后1周
        df2['d2uKey'] = np.where((a>b)&(b<c),1,0) #由向下转向上的之后1周
        df2 = df2.loc[df2['d2uKey'] == 1]
        keyList = []
        keyList = df2['date_W'].tolist()


        df['d2uLow'] = np.nan #初始化
        df['d2uHigh'] = np.nan
        df[1:2]['d2uLow'] = df[1:2]['low'] #避免有空数组，
        df[1:2]['d2uHigh'] = df[1:2]['high']
        for i in keyList:
            df['d2uLow'] = np.where(df['date_W'] == i, df['low'],df['d2uLow'])
            df['d2uHigh'] = np.where(df['date_W'] == i, df['high'],df['d2uHigh'])

        # atr通道
        add_Plot2 = [
            # 第二个蜡烛图
            mpf.make_addplot(df, type='candle', ylabel='Candle'),
            mpf.make_addplot(df[['ema21', 'ATR1', 'ATR2', 'ATR3', 'ATR-1', 'ATR-2', 'ATR-3']]),

            # 标记ema由向下转向上的第二周的最低价、最高价
            mpf.make_addplot(df['d2uLow'].tolist(), scatter=True, markersize=200, marker='_', color='r'),
            mpf.make_addplot(df['d2uHigh'].tolist(), scatter=True, markersize=200, marker='_', color='b'),  # 周线向上用蓝色



        ]
        # 设置k线图颜色
        my_color = mpf.make_marketcolors(
            up='black',  # 上涨时为红色
            down='gray',  # 下跌时为绿色
            edge='i',  # 隐藏k线边缘
            volume='in',  # 成交量用同样的颜色
            inherit=True)

        my_style = mpf.make_mpf_style(gridaxis='both',  # 设置网格
                                      gridstyle='-.',
                                      y_on_right=True,
                                      marketcolors=my_color)


        # 画atr多重通道
        mpf.plot(df,
                 title=type,
                 type='candle',
                 style=my_style,
                 volume=False,  # 交易量
                 addplot=add_Plot2,
                 # panel_ratios=(1,1),
                 figratio=(2, 1.2),  # 设置图片大小
                 # figratio=(2,3), #设置图片大小
                 figscale=3,
                 savefig=filePath + code + '_' + type + '_ATRChannel_' + '.jpg'
                 )

    return

#画图
def getChart(df, filePath,headOrTail,days,type=''):
    # 画图
    code = df.iat[1,1]#股票代码
    # df.reset_index(drop=True, inplace=True)
    df.drop(index=len(df) - 1, inplace=True)
    if headOrTail == 'tail': #从尾部取指定数量的行
        df = df.tail(days)
    if headOrTail == 'head':
        df = df.head(days)
    # df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    low5List = (df['5low'] * 0.98).tolist()
    high5List = (df['5high'] * 1.02).tolist()

    #股价偏离ema最大，绿色表示周ema向上
    low5List2 = (df['5low'] * 0.98).tolist()
    if type == 'day':
        condition = (df['ema26Trend_W'] == 'up') | (df['ema12Trend_W'] == 'up')
        df['5low2'] = np.where((df['5low'] > 0) & condition, df['5low'], np.nan) #趋势向上
        low5List2 = (df['5low2'] * 0.98).tolist()
        low5List2[0] = df['low'].tolist()[1] #避免数组空值


    #macdbar的正负值
    df['barP'] = np.where(df['bar'] > 0, df['bar'] ,0) # 取正数bar值
    df['barN'] = np.where(df['bar'] < 0, df['bar'] ,0) #取负数bar值

    #脉冲系统
    df['buyLabel'] = np.where(df['脉冲系统'] == '做多', df['high']*1.04, np.nan) #做多
    df['sellLabel'] = np.where(df['脉冲系统'] == '做空', df['low']*0.96, np.nan) #做空

    # df['bar021'] = df['bar021'] * 1.20
    bar021List = (df['bar021'] * 1.20).tolist()
    bar021List2 = (df['bar021'] * 1.20).tolist()
    lossStop2UpList = df['lossStop2'].tolist()

    # ema21向上时，强力指标在0线下，考虑做多 （不区分周线还是日线）
    df['force2Down'] = np.where((df['ema21'] > df['ema21'].shift(1)) & (df['force2'] < 0), df['force2'], np.nan)
    force2DownList = df['force2Down'].tolist()
    force2DownList[1] = df['force2'].tolist()[1] #避免数组空值，随便弄一个值

    # 标记底背离
    df.loc[df['diver'] != ' ', 'diverTemp'] = df['bar'] * 1.4
    DiverTempList = df['diverTemp'].tolist()
    DiverTempList[0] = df['bar'].tolist()[0]  # 避免空值，导致不能画图
    #标记准备底背离
    df.loc[df['diverTest'] != ' ', 'diverTemp'] = df['bar'] * 1.2
    DiverTestList = df['diverTemp'].tolist()
    DiverTestList[0] = df['bar'].tolist()[0]  # 避免空值，导致不能画图

    # 标记顶背离
    df.loc[df['diverUp'] != ' ', 'diverUpTemp'] = df['bar'] * 1.4
    DiverUpTempList = df['diverUpTemp'].tolist()
    DiverUpTempList[0] = df['bar'].tolist()[0]  # 避免空值，导致不能画图
    # 标准备记顶背离
    df.loc[df['diverUpTest'] != ' ', 'diverUpTemp'] = df['bar'] * 1.2
    DiverUpTestList = df['diverUpTemp'].tolist()
    DiverUpTestList[0] = df['bar'].tolist()[0]  # 避免空值，导致不能画图


    if type == 'day':
        condition = (df['ema26Trend_W'] == 'up') | (df['ema12Trend_W'] == 'up')         #标记周线ema向上时
        df['bar0212'] = np.where((df['bar021'] < 0) & condition, df['bar021']*1.20, np.nan)
        bar021List2 = (df['bar0212']).tolist()
        bar021List2[0] = df['bar'].tolist()[1]

        #周线向上时，止损线用蓝色，向下时用红色
        df['lossStop2Up'] = np.where(condition, df['lossStop2'], np.nan)
        lossStop2UpList = df['lossStop2Up'].tolist()
        lossStop2UpList[0] = df['low'].tolist()[1] #避免空值

        # 按日来标记周bar转向上日子，0线下在最低级标，0向上在最高价标
        df.loc[df['bar021_W2'] == 1, 'bar021_W2'] = df['low']*0.99
        bar021_W2List = df['bar021_W2'].tolist()
        bar021_W2List[0] = df['low'].tolist()[1]  # 避免空值，导致不能画图

        df.loc[df['bar021_W22'] == 1, 'bar021_W22'] = df['low']*0.99
        bar021_W22List = df['bar021_W22'].tolist()
        bar021_W22List[0] = df['low'].tolist()[1]  # 避免空值，导致不能画图
        #用蓝色标记一下周五

        # 按日来标记bar有向上转向下
        df.loc[df['bar120_W2'] == 1, 'bar120_W2'] = df['high'] * 1.01
        bar120_W2List = df['bar120_W2'].tolist()
        bar120_W2List[0] = df['high'].tolist()[1]  # 避免空值，导致不能画图



    else:
        # 按日来标记周bar转向上日子，0线下在最低级标，0向上在最高价标
        df['bar021_W2'] = np.nan #0下
        bar021_W2List = df['bar021_W2'].tolist()
        bar021_W2List[0] = df['low'].tolist()[1]  # 避免空值，导致不能画图
        df['bar021_W22'] = np.nan #0上
        bar021_W22List = df['bar021_W22'].tolist()
        bar021_W22List[0] = df['low'].tolist()[1]  # 避免空值，导致不能画图

        df['bar120_W2'] = np.nan
        bar120_W2List = df['bar120_W2'].tolist()
        bar120_W2List[0] = df['high'].tolist()[1]  # 避免空值，导致不能画图

        # df['diverTemp'] = np.nan
        # DiverTempList = df['diverTemp'].tolist()
        # DiverTempList[0] = df['bar'].tolist()[1]   # 避免空值，导致不能画图
        #
        # df['diverUpTemp'] = np.nan
        # DiverUpTempList = df['diverUpTemp'].tolist()
        # DiverUpTempList[0] = df['bar'].tolist()[1]   # 避免空值，导致不能画图

    # df['ema26+2'] = df['ema26'] * 1.02
    print(df.iat[1,0])
    add_Plot = [
        # mpf.make_addplot(df[['ema12', 'ema26', 'upC', 'downC']]),
        mpf.make_addplot(df[['ema12', 'ema26', 'upC', 'downC']]),
        mpf.make_addplot(low5List, scatter=True, markersize=40, marker='^', color='y'), #负向偏离最大
        mpf.make_addplot(low5List2, scatter=True, markersize=40, marker='^', color='g'), #仅日线时有效，ema趋势向上，偏离最大
        mpf.make_addplot(high5List, scatter=True, markersize=40, marker='v', color='r'), #正向偏离最大

        #脉冲系统，做多，做空
        mpf.make_addplot(df['sellLabel'].tolist(), scatter=True, markersize=40, marker='.', color='black'),
        mpf.make_addplot(df['buyLabel'].tolist(), scatter=True, markersize=40, marker='.', color='blue'),

        #止损点
        mpf.make_addplot(df['lossStop2'].tolist(), scatter=True, markersize=40, marker='_', color='r'),
        mpf.make_addplot(lossStop2UpList, scatter=True, markersize=40, marker='_', color='b'), #周线向上用蓝色


        #macd
        mpf.make_addplot(df['barP'], type='bar', width=0.7, panel=1, color='black'), #正数柱子
        mpf.make_addplot(df['barN'], type='bar', width=0.7, panel=1, color='dimgray'),  #负数柱子
        mpf.make_addplot(df[['dif']], panel=1, color='fuchsia', secondary_y=True),
        mpf.make_addplot(df[['dea']], panel=1, color='b', secondary_y=True),
        mpf.make_addplot(bar021List,  panel=1,scatter=True, markersize=50, marker='^', color='y'), #barKey值由-0转-1
        mpf.make_addplot(bar021List2,  panel=1,scatter=True, markersize=50, marker='^', color='g'), #barKey值由-0转-1，周线向上趋势

        # 强力指标
        mpf.make_addplot(df[['force2']],ylabel='force Index', panel=2),  # panel表示幅图，最多有9个
        mpf.make_addplot(force2DownList, scatter=True, markersize=60, panel=2, marker='.', color='g'),
        # mpf.make_addplot(df[['force2Max']], scatter=True, markersize=60, panel=2, marker='v', color='dimgray'), #最大值前10
        # mpf.make_addplot(df['force2Min'].tolist(), scatter=True, markersize=60, panel=2, marker='^', color='r'),#最小值前10


    ]


    #atr通道
    add_Plot2 = [
        # 第二个蜡烛图
        mpf.make_addplot(df, type='candle', ylabel='Candle'),
        mpf.make_addplot(df[['ema21', 'ATR1', 'ATR2', 'ATR3', 'ATR-1', 'ATR-2', 'ATR-3']]),
        mpf.make_addplot(low5List, scatter=True, markersize=40, marker='^', color='y'),  # 负向偏离最大
        mpf.make_addplot(low5List2, scatter=True, markersize=40, marker='^', color='g'),  # 仅日线时有效，ema趋势向上，偏离最大
        mpf.make_addplot(high5List, scatter=True, markersize=40, marker='v', color='gray'),  # 正向偏离最大

        # 按日来标记周bar转向上日子，0线下在最低级标，0向上在最高价标
        mpf.make_addplot(bar021_W2List, scatter=True, markersize=100, marker='.', color='r'),
        mpf.make_addplot(bar021_W22List, scatter=True, markersize=150, marker='.', color='orange'),  #0上，由向下转向上
        mpf.make_addplot(bar120_W2List, scatter=True, markersize=100, marker='.', color='y'), #由向上转向下



        # 脉冲系统，做多，做空
        mpf.make_addplot(df['sellLabel'].tolist(), scatter=True, markersize=40, marker='.', color='gray'),
        mpf.make_addplot(df['buyLabel'].tolist(), scatter=True, markersize=40, marker='.', color='gray'),

        # 止损点
        mpf.make_addplot(df['lossStop2'].tolist(), scatter=True, markersize=40, marker='_', color='r'),
        mpf.make_addplot(lossStop2UpList, scatter=True, markersize=40, marker='_', color='b'),  # 周线向上用蓝色

        # macd
        mpf.make_addplot(df['barP'], type='bar', width=0.7, panel=1, color='black'),  # 正数柱子
        mpf.make_addplot(df['barN'], type='bar', width=0.7, panel=1, color='dimgray'),  # 负数柱子
        mpf.make_addplot(df[['dif']], panel=1, color='fuchsia', secondary_y=True),
        mpf.make_addplot(df[['dea']], panel=1, color='b', secondary_y=True),
        mpf.make_addplot(bar021List, panel=1, scatter=True, markersize=50, marker='^', color='y'),  # barKey值由-0转-1
        mpf.make_addplot(bar021List2, panel=1, scatter=True, markersize=50, marker='^', color='g'),
        # barKey值由-0转-1，周线向上趋势

        # 标记底背离点
        mpf.make_addplot(DiverTestList,panel=1, scatter=True, markersize=200, marker='.', color='gray'), #准备底背离
        mpf.make_addplot(DiverTempList,panel=1, scatter=True, markersize=200, marker='.', color='r'),
        #标记顶部背离点
        mpf.make_addplot(DiverUpTestList, panel=1, scatter=True, markersize=200, marker='.', color='gray'),#准备顶背离
        mpf.make_addplot(DiverUpTempList, panel=1, scatter=True, markersize=200, marker='.', color='b'),

        # 强力指标
        mpf.make_addplot(df[['force2']], ylabel='force Index', panel=2),  # panel表示幅图，最多有9个
        mpf.make_addplot(force2DownList, scatter=True, markersize=60, panel=2, marker='.', color='g'), #


        # mpf.make_addplot(df[['force2Max']], scatter=True, markersize=60, panel=2, marker='v', color='dimgray'),
        # mpf.make_addplot(df['force2Min'].tolist(), scatter=True, markersize=60, panel=2, marker='^', color='r'),#最小值前10

    ]


    # 设置k线图颜色
    my_color = mpf.make_marketcolors(
        up='black',  # 上涨时为红色
        down='gray',  # 下跌时为绿色
        edge='i',  # 隐藏k线边缘
        volume='in',  # 成交量用同样的颜色
        inherit=True)

    my_style = mpf.make_mpf_style(gridaxis='both',  # 设置网格
                                  gridstyle='-.',
                                  y_on_right=True,
                                  marketcolors=my_color)

    mpf.plot(df,
             title= type,
             type='candle',
             style=my_style,
             volume=False, #交易量
             addplot=add_Plot,
             figratio=(2,1.2), #设置图片大小
             # figratio=(2,3), #设置图片大小
             figscale=3,
             savefig = filePath + code + '_' + type + '.jpg'
             )


    #画atr多重通道
    mpf.plot(df,
             title=type,
             type='candle',
             style=my_style,
             volume=False, #交易量
             addplot=add_Plot2,  #多重通道
             # panel_ratios=(1,1),
             figratio=(2,1.2), #设置图片大小
             # figratio=(2,3), #设置图片大小
             figscale=3,
             savefig = filePath + code + '_' + type + '_ATRChannel_' + '.jpg'
             )

    # mpf.plot(df,
    #          title=code + '_' + type,
    #          type='candle',
    #          style=my_style,
    #          volume=False, #交易量
    #          addplot=add_Plot,
    #          figratio=(2,1.2), #设置图片大小
    #          # figratio=(2,3), #设置图片大小
    #          figscale=3,
    #          savefig = filePath + code + '_' + type + '.jpg'
    #          )

    # mpf.show()

    # 下面方法可以访问美股
    # data = pdr.get_data_yahoo('IBM', '2020/9/1', '2020/10/1')
    # mpf.plot(data,type='candle')
    # mpf.plot(data, type='ohlc', mav=4)

#判断底部背离数据
def getDivergence(df, i, bar021Array, closeArray, barArray):
    if i == 0:
        df['diver'] = ' '  #初始化
        df['diverTest'] = ' '  #初始化
    bar021 = bar021Array[i]
    close = closeArray[i]
    if bar021 < 0: #这个从下转向上的点存在
        for j in range(1,150):  #向上循环7个月
            if i - j > 0:
                bar021Previous = bar021Array[i-j]
                closePrevious = closeArray[i-j]
                if bar021Previous < 0 and bar021Previous < bar021 and closePrevious > close: #找到股价比当前高，但bar柱比当前长日期
                    # print('这日期有背离：' + str(df.at[i,'date']) + '，之前日期点是：' + str(df.at[i-j,'date']))
                    df.at[i,'diver'] = df.at[i,'diver'] + ',' + df.at[i-j,'date']

    #把每天的bar值都跟之前bar021比较，看看底背离情况
    bar = barArray[i]
    if bar < 0:
        for x in range(1,150):
            if i - x > 0:
                barPrevious = barArray[i-1]
                bar021Previous = bar021Array[i-x]
                closePrevious = closeArray[i-x]
                if bar021Previous < 0 and bar021Previous < bar and closePrevious > close and bar < barPrevious:
                    df.at[i, 'diverTest'] = df.at[i, 'diverTest'] + ',' + df.at[i - x, 'date']
    return  df



#判断顶部背离数据
def getDivergenceUp(df, i, bar120Array, closeArray, barArray):
    if i == 0:
        df['diverUp'] = ' '  #初始化
        df['diverUpTest'] = ' '  #初始化
    bar120 = bar120Array[i]
    close = closeArray[i]
    if bar120 > 0: #这个从下转向上的点存在
        for j in range(1,65):  #向上循环7个月
            if i - j > 0:
                bar120Previous = bar120Array[i-j]
                closePrevious = closeArray[i-j]
                if bar120Previous > bar120 and closePrevious < close: #找到股价比当前低，但bar柱比当前长日期
                    # print('这日期有背离：' + str(df.at[i,'date']) + '，之前日期点是：' + str(df.at[i-j,'date']))
                    df.at[i,'diverUp'] = df.at[i,'diverUp'] + ',' + df.at[i-j,'date']
    #把每天的bar值都跟之前bar120比较，看看顶背离情况
    bar = barArray[i]
    if bar > 0:
        for x in range(1,65):
            if i - x > 0:
                barPrevious = barArray[i-1]
                bar120Previous = bar120Array[i-x]
                closePrevious = closeArray[i-x]
                if bar120Previous > 0 and bar120Previous > bar and closePrevious < close and bar > barPrevious:
                    df.at[i, 'diverUpTest'] = df.at[i, 'diverUpTest'] + ',' + df.at[i - x, 'date']
    return  df


#判断当天是否为最近5天最合适卖（以ema26为基准）
def getSellPointBaseEma26(df, i, highDifEma26Array, days=4):
    #先把最低价放入数组，方便后面使用
    if len(highDifEma26Array) == 0:
        df['highDifEma26'] = df['high'] - df['ema26']
        highDifEma26Array = df['highDifEma26'].values
        del df['highDifEma26']
    if i > days:
        a = df.at[i,'date']
        ema26 = df.at[i,'ema26']
        today = highDifEma26Array[i]
        temp = highDifEma26Array[i-days:i+1]
        max  = highDifEma26Array[i-days:i+1].max()
        if today == max:
            df.at[i, '5high'] = df.at[i,'high']
    return [df, highDifEma26Array]


#判断当天是否为最近5天最合适买点（以ema26为基准）
def getBuyPointBaseEma26(df, i, lowDifEma26Array, days=4):
    #先把最低价放入数组，方便后面使用
    if len(lowDifEma26Array) == 0:
        df['lowDifEma26'] = df['low'] - df['ema26']
        lowDifEma26Array = df['lowDifEma26'].values
        del df['lowDifEma26']
    if i > days:
        today = lowDifEma26Array[i]
        min  = lowDifEma26Array[i-days:i+1].min()
        if today == min:
            df.at[i, '5low'] = df.at[i,'low']
    return [df, lowDifEma26Array]


#计算止损价（每天计算），下降取30天回溯期，差值系数为2；上升取40天回溯期，差值系数为3
def getLossStopPrice(df,i,lowDiffArray):
    #以当天ema12为基准确定是上升还是下降，然后执行不同逻辑。

    #先把最低价放入数组，方便后面使用
    if len(lowDiffArray) == 0:
        df['lowDiff'] = df['low'] - df['low'].shift(1) #计算差值
        lowDiffArray = df['lowDiff'].values
        del df['lowDiff']


    if i > 0:
        # 确定一下系数
        if df.at[i,'ema12'] > df.at[i-1,'ema12']:   #ema12向上
            days = 40
            factor = 3 #差值系数
        else:
            days = 30
            factor = 2
        #计算止损
        if i > days:
            lowPriceTemp = lowDiffArray[i-days:i]
        else:
            lowPriceTemp = lowDiffArray[0:i]
        y = 0
        sum = 0
        for x in lowPriceTemp:
            if x < 0:
               sum = sum +abs(x)
               y = y + 1
        if y > 0:
            avg = sum/y
            df.at[i+1,'code'] = df.at[i,'code']
            # df.at[i+1,'date'] = df.at[i,'date']
            df.at[i+1,'lossStop'] = df.at[i,'low'] - avg*factor
            df.at[i + 1, 'lossStop2'] = max(df.at[i + 1, 'lossStop'], df.at[i, 'lossStop'],df.at[i - 1, 'lossStop']) #防止止损点下拉，设定取3天内最高止损点
            # test = df.at[i,'low']
            # test2 = df.at[i+1,'lossStop']
        # if i == 100:
        #     outPutXlsx(df)
        #     fd = 33
    return [df, lowDiffArray]



# 当bar为负，计算在一周期内，由'-0'转'-1'的次数，方便后续全网做排序，选次数多的来买
def getBarChangeCount(df,i,barChangeCount):
    if i > 10 and df.at[i-1,'bar'] > 0 and df.at[i,'bar'] < 0 : #选择bar值为负的周期
        barChangeCount = 0
    if barChangeCount > 0 and df.at[i,'bar'] < 0 : #补全不是转化当天的日期，方便后面统计
        df.at[i, 'barKeyCh'] = barChangeCount
    if i > 10 and df.at[i-1,'barKey'] == '-0' and df.at[i,'barKey'] == '-1':
        barChangeCount += 1
        df.at[i,'barKeyCh'] = barChangeCount
    return [df, barChangeCount]


#计算股票偏离ema26的程度
def getPriceDifEma26(df):

    #以股价-ema26的值跟通道值比较，得到占通道比例，然后做个排序


    return


#计算ATR的3倍通道：基线是ema21，atr是10周期
def getATRChannel(df):

    df['price1'] = df['high'] - df['low']
    df['price2'] = df['high']- df['close'].shift(1)
    df['price3'] = df['close'].shift(1) - df['low']
    df['TR'] = df[['price1', 'price2','price3']].max(axis=1)
    del df['price1']
    del df['price2']
    del df['price3']

    df['ATR'] = pd.DataFrame.ewm(df['TR'], span=14).mean() #用ema21平滑，长期趋势
    df['ema21'] = pd.DataFrame.ewm(df['close'], span=21).mean() #用ema21平滑，长期趋势
    df['ema21Trend'] = np.where(df['ema21'] > df['ema21'].shift(1), 'up', 'down')

    df['ATR1'] = df['ema21'] + df['ATR']
    df['ATR2'] = df['ema21'] + df['ATR']*2
    df['ATR3'] = df['ema21'] + df['ATR']*3
    df['ATR-1'] = df['ema21'] - df['ATR']
    df['ATR-2'] = df['ema21'] - df['ATR']*2
    df['ATR-3'] = df['ema21'] - df['ATR']*3

    # 简单预测明天通道价格
    index = len(df)
    df.at[index - 1, 'ATR1'] = df.iloc[index - 2]['ATR1'] * 2 - df.iloc[index - 3]['ATR1']
    df.at[index - 1, 'ATR2'] = df.iloc[index - 2]['ATR2'] * 2 - df.iloc[index - 3]['ATR2']
    df.at[index - 1, 'ATR3'] = df.iloc[index - 2]['ATR3'] * 2 - df.iloc[index - 3]['ATR3']
    df.at[index - 1, 'ATR-1'] = df.iloc[index - 2]['ATR-1'] * 2 - df.iloc[index - 3]['ATR-1']
    df.at[index - 1, 'ATR-2'] = df.iloc[index - 2]['ATR-2'] * 2 - df.iloc[index - 3]['ATR-2']
    df.at[index - 1, 'ATR-3'] = df.iloc[index - 2]['ATR-3'] * 2 - df.iloc[index - 3]['ATR-3']
    df.at[index - 1, 'ema21'] = df.iloc[index - 2]['ema21'] * 2 - df.iloc[index - 3]['ema21']
    # del df['TR']
    # del df['ema21']
    # del df['ATR']
    return df



#计算脉冲系统
def getPulseSystem(df):
    # print(df)
    # exit()

    # df['c/ema26'] = df['close'] / df['ema26'] - 1
    #
    # df['h/ema26%'] = (df['high'] / df['ema26'] - 1) * 100
    # df['h/ema26%'] = df['h/ema26%'].round(0)
    #
    # df['c/ema26%'] = (df['close'] / df['ema26'] - 1) * 100
    # df['c/ema26%'] = df['c/ema26%'].round(0)
    #
    # df['l/ema26%'] = (df['low'] / df['ema26'] - 1) * 100
    # df['l/ema26%'] = df['l/ema26%'].round(0)
    #
    #
    #
    # df['c/Channel'] = df['c/ema26'] / df['upCFactor'] * 10  #收盘价在通道的比例
    # df['c/Channel'] = df['c/Channel'].round(1)
    #
    # df['h/Channel'] = (df['high'] / df['ema26'] - 1) / df['upCFactor'] * 10 #最高价在通道的比例
    # df['h/Channel'] = df['h/Channel'].round(1)
    #
    # df['l/Channel'] =(df['low'] / df['ema26'] - 1) / df['upCFactor']  * 10 #最低价在通道的比例
    # df['l/Channel'] = df['l/Channel'].round(1)

    df['force'] = (df['close'] - df['close'].shift(1)) * df['volume']  #强力指数
    df['force2'] = pd.DataFrame.ewm(df['force'], span=2).mean()  #用ema2平滑，短期交易识别
    maxValue = df['force2'].max()
    df['force2'] = df['force2']/maxValue * 100

    # 找到force2最大10个值、最小10个值
    df2 = df.nlargest(20, 'force2')
    listLarge = df2.index.values.tolist()
    for i in listLarge:
        df.at[i,'force2Max'] = df.at[i,'force2']

    df2 = df.nsmallest(20, 'force2')
    listSmall = df2.index.values.tolist()
    for i in listSmall:
        df.at[i,'force2Min'] = df.at[i,'force2']

    # print(df)

    # df = df.head(10)
    # df2 = df.nsmallest(1, 'force2')
    # # exit()
    # df2['force2Max'] = 1
    # print(df)

    # df3 = df2.loc[:,'force2Max']
    # df = pd.merge(df, df2, how='left')  # 合并 （把处理过的值何合入原来df）
    # df = pd.merge(df, df2)  # 合并 （把处理过的值何合入原来df）



    # df2 = df.nsmallest(10, 'force2')
    # df2['force2Min'] = df2['force2']
    # df = pd.merge(df, df2, how='left')  # 合并 （把处理过的值何合入原来df）



    df['ema12Trend'] = np.where(df['ema12'] > df['ema12'].shift(1), 'up', 'down')
    df['ema26Trend'] = np.where(df['ema26'] > df['ema26'].shift(1), 'up', 'down')
    condition = (df['barKey'] == '1') | (df['barKey'] == '-1')
    condition2 = (df['barKey'] == '0') | (df['barKey'] == '-0')
    df['脉冲系统'] = np.where((df['ema12Trend'] == 'up') & condition, '做多', '')
    df['脉冲系统'] = np.where((df['ema12Trend'] == 'down') & condition2, '做空', df['脉冲系统'])
    return df


def formatPrecentStr2Float(df):
    df = df.str.strip("%").astype(float) / 100       # df['增幅'] = df['增幅'].str.strip("%").astype(float) / 100
    return df

def formatFloat2PrecentStr(df):
    df = df.apply(lambda x: format(x, '.2%'))   #df["增幅"] = df["增幅"].apply(lambda x: format(x, '.2%'))
    return df

 #计算通道（4个月95%线柱包含在通道内）
def getEma26Channel(df,i,ema26DiffArray):

    #计算通道（4个月95%线柱包含在通道内）
    #新算法： 1）先把每天相对均线的最大值计算出来，并且放入array. 2)从当前位置取最近100个值，然后排序，取95%位置左右的值. 3)找到该值对应的ema26值，计算因子。 4）然后用这个因子更新当前i行的通道值。
    # 找到每天的k线相对均线的最大值 （从最高价-均线，最低价-均线，取两者绝对值的最大值
    if len(ema26DiffArray) == 0:
        df['high-ema26'] = np.where(
            abs(df['high'] - df['ema26']) - abs(df['low'] - df['ema26']) > 0,
            abs(df['high'] - df['ema26']),
            abs(df['low'] - df['ema26']) )
        ema26DiffArray = df['high-ema26'].values
        # printEma26Array = df['ema26'].values #

    number = 60 #取最近100个K线
    if i > number:
        priceArrayNew = ema26DiffArray[i-number:i+1]
        # printEma26Array = printEma26Array[i-100:i+1] #
    else:
        priceArrayNew = ema26DiffArray[0:i+1]
        # priceArrayNew = priceArray[0:i]

    sum = len(priceArrayNew)
    goal = int(sum * 0.94)
    # print(i)
    priceArrayNew2 = np.sort(priceArrayNew) #排序
    upCValue = priceArrayNew2[goal-1]  #找到临界点的那个值
    #计算通道因子
    upCValueId = np.where(priceArrayNew==upCValue)[0][0]
    upCEma26Id = i - (sum -  upCValueId) + 1  #找到该临界值在df的id
    upCEma26 = df.at[upCEma26Id,'ema26']
    upCFactor = upCValue/upCEma26

    df.at[i,'upCFactor'] = upCFactor
    df.at[i,'upC'] = df.at[i,'ema26'] * (1+upCFactor)
    df.at[i,'downC'] = df.at[i,'ema26'] * (1-upCFactor)

    # if i == 232:
    #     df = df[['date', 'open', 'high', 'low', 'ema26','high-ema26','upC','downC']]
    #     outPutXlsx(df)

        # print('11111')
        # exit()
        # print(priceArrayNew)
        # exit()
        # df = df[['date', 'open', 'high', 'low', 'ema26','high-ema26']]
        # print(priceArray)
        # print(len(priceArray))
        # print(priceArrayNew)
        # print(len(priceArrayNew))
        # print(priceArrayNew2)
        # print('切片元素个数：' + str(sum))
        # print('95%对于数量：' + str(goal))
        # print('这个切片的通道临界值：' + str(upCValue))
        # # print(printEma26Array[upCema26Id])
        # print(upCValueId)



        # print(df.at[i,'date'])
        # print(df.at[i,'ema26'])
        # print(upCValue/df.at[i,'ema26']-1)
        # outPutXlsx(df)

    return [df,ema26DiffArray]


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


def outPutXlsx(df,name='temp'):
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    path = '/Users/miketam/Downloads/'+ today + '/'+ name + '.xlsx'
    df.to_excel(path, float_format='%.5f',index=False)


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

    #标记bar柱零线下从向下转向上，主要用于手工识别背离
    df['bar021'] =  np.where((df['bar'].shift(-1) > df['bar']) & (df['bar'].shift(1) > df['bar']) & (df['bar'] < 0) , df['bar'], np.nan)
        #注意只要1条，2条，

    #标记bar柱0线上，由向上转向下，主要用于识别顶部背离
    df['bar120'] = np.where((df['bar'].shift(-1) < df['bar']) & (df['bar'].shift(1) < df['bar']) & (df['bar'] > 0) , df['bar'], np.nan)

    #当股价下跌，bar值却增大，证明股价
    # df['barReduce'] =


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


def mkdir(path):
    folder = os.path.exists(path)

    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径


