import datetime
import pandas as pd
import openpyxl
import numpy as np
import time
import os


#股价大于某均线
def aboveEma(df, line):

    return


#买入后，固定天数卖出
def daySell(df,i,days, goal):
    days = days + 1
    if df.at[i, 'signal'] == 1:  # 如果两个信号间隔少于5天，即在第二个信号后5天才卖出
        days = 1
    if days == goal:
        df.at[i, 'signal'] = 0  # 买入第5天后产生卖出信号
    return df,days


#止损卖出
def lossStopSell(df,i,pos,lossStopPrice,buyDate):
    # 止损卖出（止损卖出是当天发生，所以这里判断止损后要修改前一天的signal; 止损逻辑要比下面判断天数卖出要前）
    if i > 0 and df.at[i - 1, 'signal'] == 1 and pos == 0:  # 昨天买入标记（今天买入）
        # print(i)
        # print(df.at[i,'date'])
        # print('第一个买入信号')
        # lossStopPrice = df.at[i,'lossStop2']  #记录今天止损价，方便后续使用
        lossStopPrice = df.at[i, 'lossStop2']  # 记录今天止损价，方便后续使用
        pos = 1  # 表明是持仓状态
        buyDate = df.at[i, 'date']

    # 持仓时，每天监控是否止损
    if df.at[i, 'low'] < lossStopPrice and df.at[i, 'high'] > lossStopPrice and pos == 1 and df.at[
        i, 'date'] != buyDate:
        # print(i)
        # print(df.at[i,'date'])
        # print('止损')
        # exit()
        df.at[i, 'sellPrice'] = lossStopPrice  # 止损价卖出
        df.at[i - 1, 'signal'] = 0  # 标记卖出信号
        df.at[i, 'lossStop'] = 1  # 用作表明是止损卖出
        # df.at[i,'lossStopXX'] = lossStopPrice  #用作表明是止损卖出
        pos = 0  # 不持仓

    # 没有触发止损，在计划天数卖出
    if i > 0 and df.at[i - 1, 'signal'] == 0:
        pos = 0

    return df,pos,lossStopPrice,buyDate


#止盈卖出
def winStopSell(df,i,pos,buyPrice,buyDate):
    # 止盈逻辑
    if i > 0 and df.at[i - 1, 'signal'] == 1 and pos == 0:  # 昨天买入标记（今天买入）
        pos = 1  # 表明是持仓状态
        buyDate = df.at[i, 'date']
        buyPrice = df.at[i, 'close']

    # 每天监控是否止盈
    lossStopPrice = df.at[i, 'lossStop2']
    if df.at[i, 'low'] < lossStopPrice and df.at[i, 'high'] > lossStopPrice and pos == 1 and df.at[
        i, 'date'] != buyDate and lossStopPrice > buyPrice:
        # if df.at[i,'low'] < lossStopPrice and df.at[i,'high'] > lossStopPrice and pos == 1 and df.at[i,'date'] != buyDate:
        # print(i)
        # print(df.at[i,'date'])
        # print('止损')
        # exit()
        df.at[i, 'sellPrice'] = lossStopPrice  # 止损价卖出
        df.at[i - 1, 'signal'] = 0  # 标记卖出信号
        df.at[i, 'lossStop'] = 2  # 用作表明是止盈卖出
        # df.at[i,'lossStopXX'] = lossStopPrice  #用作表明是止损卖出
        pos = 0  # 不持仓
        buyPrice = 0
    # #没有触发止损，在计划天数卖出
    if i > 0 and df.at[i - 1, 'signal'] == 0:
        pos = 0

    return df, pos, buyPrice, buyDate
