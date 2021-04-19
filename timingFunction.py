import pandas as pd
import openpyxl
import numpy as np
from func import *

# -*- coding: utf-8 -*-
"""
@author: Xingbuxing
date: 2017年05月06日
汇总择时策略需要用到的一些常见函数
"""


# 根据交易信号，计算每天的仓位
def position(df):
    """
    根据交易信号，计算每天的仓位
    :param df:
    :return:
    """
    # 由signal计算出实际的每天持有股票仓位
    df['pos'] = df['signal'].shift() #有交易信息，第二天才会买入
    df['pos'].fillna(method='ffill', inplace=True)

    # 将涨跌停时不得买卖股票考虑进来
    # 找出开盘涨停的日期
    cond_cannot_buy = df['open'] > df['close'].shift(1) * 1.097  # 今天的开盘价相对于昨天的收盘价上涨了9.7%
    # 将开盘涨停日、并且当天position为1时的'pos'设置为空值
    df.loc[cond_cannot_buy & (df['pos'] == 1), 'pos'] = None

    # 找出开盘跌停的日期
    cond_cannot_sell = df['open'] < df['close'].shift(1) * 0.903  # 今天的开盘价相对于昨天的收盘价下得了9.7%
    # 将开盘跌停日、并且当天position为0时的'pos'设置为空值
    df.loc[cond_cannot_sell & (df['pos'] == 0), 'pos'] = None

    # position为空的日期，不能买卖。position只能和前一个交易日保持一致。
    df['pos'].fillna(method='ffill', inplace=True)

    # 在position为空值的日期，将position补全为0
    df['pos'].fillna(value=0, inplace=True)

    return df


# 计算资金曲线，简单版本
def equity_curve_simple(df):
    """
    最简单的计算资金曲线的方式，与实际不符合
    :param df:
    :return:
    """

    # ===计算实际资金曲线
    # 当当天空仓时，pos为0，资产涨幅为0
    # 当当天满仓时，pos为1，资产涨幅为股票本身的涨跌幅
    df['equity_change'] = df['涨跌幅'] * df['pos']
    # 根据每天的涨幅计算资金曲线
    df['equity_curve'] = (df['equity_change'] + 1).cumprod()

    return df


# 计算资金曲线，简单版本
def equity_curve(df, initial_money=100000, slippage=0.01, c_rate=5.0/10000, t_rate=1.0/1000):
    """
    :param df:
    :param initial_money: 初始资金，默认为1000000元
    :param slippage: 滑点，默认为0.01元
    :param c_rate: 手续费，commission fees，默认为万分之5
    :param t_rate: 印花税，tax，默认为千分之1
    :return:
    """

    # ===第一天的情况
    df.at[0, 'hold_num'] = 0  # 持有股票数量
    df.at[0, 'stock_value'] = 0  # 持仓股票市值
    df.at[0, 'actual_pos'] = 0  # 每日的实际仓位
    df.at[0, 'cash'] = initial_money  # 持有现金现金
    df.at[0, 'equity'] = initial_money  # 总资产 = 持仓股票市值 + 现金

    #计算交易次数，盈亏

    # ===第一天之后每天的情况
    for i in range(1, df.shape[0]):

        # 前一天持有的股票的数量
        hold_num = df.at[i - 1, 'hold_num']
        # 若发生除权，需要调整hold_num
        # if abs((df.at[i, 'close'] / df.at[i - 1, 'close'] - 1) - df.at[i, '增幅']) > 0.001:
        #     print('发生除权？ 在我这里应该不会发生')
        #     stock_value = df.at[i - 1, 'stock_value']
        #     last_price = df.at[i, 'close'] / (df.at[i, '增幅'] + 1)
        #     hold_num = stock_value / last_price
        #     hold_num = int(hold_num)

        # 判断是否需要调整仓位
        # 需要调整仓位
        if df.at[i, 'pos'] != df.at[i - 1, 'pos']:
            # 昨天的总资产 * 今天的仓位 / 今天的收盘价，得到需要持有的股票数
            theory_num = df.at[i - 1, 'equity'] * df.at[i, 'pos'] / df.at[i, 'close']
            # 对需要持有的股票数取整
            # print(i)

            theory_num = int(theory_num)  # 向下取整数
            # 判断加仓还是减仓
            # 加仓
            if theory_num >= hold_num:
                # 计算实际需要买入的股票数量
                buy_num = theory_num - hold_num
                # 买入股票只能整百，对buy_num进行向下取整百
                buy_num = int(buy_num / 100) * 100

                # 计算买入股票花去的现金
                # buy_cash = buy_num * (df.at[i, 'open'] + slippage)
                buy_cash = buy_num * (df.at[i, 'close'] + slippage)  #收盘价买入
                # 计算买入股票花去的手续费，并保留2位小数
                commission = round(buy_cash * c_rate, 2)
                # 不足5元按5元收
                if commission < 5 and commission != 0:
                    commission = 5
                df.at[i, '手续费'] = commission

                # 计算当天收盘时持有股票的数量和现金
                df.at[i, 'hold_num'] = hold_num + buy_num  # 持有股票
                df.at[i, 'cash'] = df.at[i - 1, 'cash'] - buy_cash - commission  # 剩余现金

            # 减仓
            else:
                # 计算卖出股票数量，卖出股票可以不是整数，不需要取整百。
                sell_num = hold_num - theory_num

                # 计算卖出股票得到的现金
                # sell_cash = sell_num * (df.at[i, 'open'] - slippage)
                # sell_cash = sell_num * (df.at[i, 'close'] - slippage)   #收盘价卖出
                sell_cash = sell_num * (df.at[i,'sellPrice'] - slippage)   #专门的卖出价列
                # 计算手续费，不足5元按5元收并保留2位小数
                commission = round(max(sell_cash * c_rate, 5), 2)
                df.at[i, '手续费'] = commission
                # 计算印花税，保留2位小数。历史上有段时间，买入也会收取印花税
                tax = round(sell_cash * t_rate, 2)
                df.at[i, '印花税'] = tax

                # 计算当天收盘时持有股票的数量和现金
                df.at[i, 'hold_num'] = hold_num - sell_num  # 持有股票
                df.at[i, 'cash'] = df.at[i - 1, 'cash'] + sell_cash - commission - tax  # 剩余现金

        # 不需要调仓
        else:
            # 计算当天收盘时持有股票的数量和现金
            df.at[i, 'hold_num'] = hold_num  # 持有股票
            df.at[i, 'cash'] = df.at[i - 1, 'cash']  # 剩余现金

        # 计算当天的各种数据
        df.at[i, 'stock_value'] = df.at[i, 'hold_num'] * df.at[i, 'close']  # 剩余现金
        df.at[i, 'equity'] = df.at[i, 'cash'] + df.at[i, 'stock_value']  # 总资产
        df.at[i, 'actual_pos'] = df.at[i, 'stock_value'] / df.at[i, 'equity']  # 实际仓位
    return df

#评估择时策略
def timingEvaluate(df, dfResult):
    #交易次数（买+卖），胜率，平均涨幅，累计盈亏，累计税费，；统计时长，交易天数，年化盈亏率，
    #最大亏损，最大亏损开始时间，最大盈利，最大盈利开始时间

    #交易次数
    print(df.at[1,'code'])
    df2 = df.loc[df['印花税'] > 0]
    tradeCount = len(df2)
    print("---统计数据开始-----")
    print("交易次数：" + str(tradeCount))

    #提取有交易的日期形成新的df简化显示，同时计算上面的参数
    condition = (df['手续费'] > 0) &(np.isnan(df['印花税']) == True )
    df.loc[condition,'b/s'] = 'buy'
    condition = (df['手续费'] > 0) &(df['印花税'] > 0)
    df.loc[condition,'b/s'] = 'sell'
    # outPutXlsx(df,'择时策略-完整数据(每天记录)')  #占用很多时间
    df = df.loc[(df['b/s'] == 'buy') | (df['b/s'] == 'sell')] #只显示有交易的日期
    #如果最后一行是buy，就删除（因为不是完整交易）
    if df.iloc[-1]['b/s'] == 'buy':
        df.drop(df.tail(1).index, inplace=True)

        #计算胜率
    # df['w/l'] = df['equity'] - df['equity'].shift(1)
    df['w/l'] = df['equity'].diff()/df['equity'].shift()
    df.loc[(df['w/l'].shift(-1) > 0), 'w/l2'] = '盈利'

    df.loc[df['b/s'] == 'buy','w/l'] = np.nan
    winCount = len(df.loc[df['w/l'] > 0])
    lossCount = len(df.loc[df['w/l'] < 0])
    totalCount = winCount + lossCount
    print('胜率：' + str(winCount/totalCount))


    #累计盈利
    initial_money = 100000
    df2 = df.loc[(df['b/s']== 'sell'),'equity']
    equity = df2.tolist()[-1]
    profit = equity/initial_money - 1
    print('累计盈利率：' + str(profit))

    #累计税费
    fee = df['手续费'].sum()
    tax = df['印花税'].sum()
    print('累计手续费：' + str(fee))
    print('累计印花税：' + str(tax))
    print('累计税费率：' + str(((tax+fee)/initial_money - 1)/100))

    #交易周期，持仓天数，年化收益率
    # time = pd.to_datetime(df.at[0,'date'])
    # df.reset_index(inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    start = df['date'].tolist()[0]
    end = df.loc[df['b/s'] == 'sell','date'].tolist()[-1]
    # end = df['date'].tolist()[-1]
    time = end - start
    time = time.days
    print('累计投资时长：' + str(time))

    # df['holdingTime'] = df['date'] - df['date'].shift(1)
    df['holdingTime'] = df['date'].diff()
    df.loc[df['b/s'] == 'buy','holdingTime'] = np.nan
    df['holdingTime'] = df['holdingTime'].apply(lambda x:x.days)
    holdingTime = df['holdingTime'].sum()
    print('累计持仓时长：' + str(holdingTime))
    # 整理得到：年华收益 = pow(总收益, 365/天数) - 1

    #股价量化增长
    priceBegin = df.iloc[0]['close']
    priceEnd = df.iloc[-1]['close']
    # print(priceBegin)
    # print(priceEnd)
    priceYear =  pow(priceEnd/priceBegin, 365.0/time)- 1
    print('股价年化增长：' + str(priceYear))

    earningYear = pow(1 + profit, 365.0/holdingTime)- 1
    print('投资年化收益：' + str(earningYear))




    df['date'] = df['date'].dt.strftime('%Y-%m-%d')    #把时间修改为字符格式

    #最大亏损
    df2 = df.loc[df['b/s']== 'sell']
    maxLoss_end_date, max_loss,equity = tuple(df2.sort_values(by=['w/l']).iloc[0][['date', 'w/l','equity']])
    print('最大亏损日期：' + str(maxLoss_end_date))
    print('最大亏损率：',max_loss)

    #最大盈利
    maxWin_end_date, max_win,equity = tuple(df2.sort_values(by=['w/l']).iloc[-1][['date', 'w/l','equity']])
    print('最大盈利日期：' + str(maxWin_end_date))
    print('最大盈利率：',max_win)


    dfResult = dfResult.append({'code': df.iloc[0]['code'],
                                '交易次数': tradeCount,
                                '胜率': winCount/totalCount,
                                '累计盈利率': profit,
                                '年化收益': earningYear,
                                '股价年化增长':priceYear,
                                '投资时长': time,
                                '持仓时间':holdingTime,
                                '最大亏损': max_loss,
                                '亏损日期':str(maxLoss_end_date),
                                '最大盈利':max_win,
                                '盈利日期':str(maxWin_end_date),
                                }, ignore_index=True)

    return [df,dfResult]


