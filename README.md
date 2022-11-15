
# The analysis of Stock Price Patterns

## **Project Introduction**

This project was born when I began to learn about investing in shares. I read some books, such as "Trading for Living" which mentioned various trading signals based on stock chart analysis. So I hoped to use the program to help analyze the stock chart data and filter stocks with trading signals. Example of signals: the MACD bar deviates, the stock price breaks through the ATR channel, the MACD Bar turns downward to upward, the price breaks through the stop loss line, the weekly stock price deviates too much from the EMA...

After generating the signal, I displayed the signal with charts. Later,

To verify whether the trading strategies based on signals are reliable or not, I did the program to test the success rate and the profit margin. The above is in essence the function of this project.

As this is a personal project and an iterative project, the design of the code structure is not good. Moreover, having known more stock analysis tools. I found that professional stock analysis tools can meet my requirements for stock chart analysis. So, for personal investors, it is better to use professional tools to analyze stocks than to develop tools on their own. These tools can provide various analyses and custom functions, and there is no need to spend time developing tools by themselves.

Of course, there are also specific or personalized situations. For example, I did another project that got the number of pocket pivot stocks in a stock sector, because it cannot be obtained with professional stock tools.

## **Program process steps:**

1. Get the K-line data of the desired stock from the stock data platform through the API and save it locally.
2. Process the k-line data, such as calculating the moving average, MACD, ATR channel, KDJ, stop loss line, etc.
3. Implement various strategy signal logic, such as MACD bar divergence, stock price breaking through the ATR channel, price breaking through the stop loss line…
4. According to the backtesting of the historical data, calculate the winning rate and the rate of profit.
5. According to the historical data of the signal backtesting stock, get the approximate situation of winning rate and profit and loss.
6. Call the Mplfinance drawing library to generate stock price charts and strategy signal images.
7. Export stock selection results for different strategies, and export the Excel list.

## **Technology applied to the project:**

1. panda: handles all the work from getting stock data to processing data analysis.
2. mplfinance: generate K-line, Macd, and other charts from each stock, and flag various trading strategy signals on the chart.

## **Experience from the project:**

This project is my first project that uses pandas for data analysis. It is a project with continuous iteration of ideas, and the duration of the whole project is almost a year. The entire project code is about 6k lines. And through the project, I have mastered some common functions of pandas, such as:

- Data selection method: loc, iloc, iat, at, tail…
- Data processing: tolist, drop, drop_duplicates, fillna, merge, append, join, groupby, set_index, Series…
- File handling: read_csv, to_excel…
- Drawing: mplfinance

the downside of this project is that I did not fully consider the application modularity at the beginning. Due to the continuous superposition of the following functions, the code is embedded in many levels, which is not easy to read and maintain. Besides, I experienced difficulties in data processing performance. The logic of processing and storing data still leaves a lot of room for optimization.

In general, as my first data processing and analysis project, I have learned a lot from here. I learned to verify my ideas through programming. From the project, I mastered some basic knowledge and applications of scientific computing.

## **Precautions:**

This project is a complete development project that can be run directly locally. The functional logic and signal strategy in it are based on my thinking, and others may not apply. If you are interested in the project, you can download it locally to check the code, and extract some code or ideas that may be of a reference value.

## **Some screenshots of the project:**

1 In the figure below showed the files outputed from the project. The "chart" folder was the charts of stock price patterns and the trading signals. The Excel files were the lists of stocks that filtered by the different strategies.
![1](https://user-images.githubusercontent.com/5052733/201301299-8123a445-9a17-4e50-802e-6c185fc53dc8.png)
 
 
 
2 The files in "chart" folder  are the stocks charts and the trading signals.
![8-stock-list](https://user-images.githubusercontent.com/5052733/201443477-991c19cf-c4db-4941-96d3-e66a939d0486.png)

3 In the figure below, It showed the charts and signals that generated according to the rules I defined. The figure was divided into three parts: the upper part was the signal of ATR channel, the stop loss line and the price deviation. The middle part was the signal of macd bar deviation. The lower part was the signal of strong indicator.
![2-day chart](https://user-images.githubusercontent.com/5052733/201303918-5f20b3e6-8554-4645-b36b-d2721da5879d.png)
![3-day chart2](https://user-images.githubusercontent.com/5052733/201303951-b9ca45c1-139c-4225-8b44-7f93ebc3583d.png)

4 In the figures below, It showed the stock selection results for different strategies.
![6-excel](https://user-images.githubusercontent.com/5052733/201304066-8b4c1a3a-85bd-4fd4-be45-14f0c02e8ae0.png)

![5-周背离](https://user-images.githubusercontent.com/5052733/201304107-1ac514ed-1d91-47c3-95d1-a212b1a112ba.png)

![7-excel-周趋势向上](https://user-images.githubusercontent.com/5052733/201304139-2759bf86-6f10-400f-a1cb-3e8b1e7d3c3d.png)
