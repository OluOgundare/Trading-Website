#import dataframes
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import yfinance as yf

plt.style.use('fivethirtyeight')
plt.rcParams["font.family"] = "monospace"
plt.rcParams['font.size'] = 20

def stock_info(stock, period, EMA_minimum_periods, smoothing_factor, SDs, startDate, endDate):
    plt.figure(figsize = (20, 10))
    # Getting the data TSLA
    stock_data = yf.download(stock, startDate, endDate)
    #Getting general information about the company
    information = yf.Ticker(stock)
    try:
        company_name = information.info['shortName']
    except:
        company_name = stock
    try:
        company_website = information.info['website']
    except:
        company_website = "https://finance.yahoo.com/"

    # Plot the close price of the stock
    plt.plot(stock_data['Adj Close'], color = "darkblue", label = "Close Price", linewidth = 2)
    plt.grid(False)
    plt.xlabel("Date")
    plt.ylabel("Close Price (USD)")
    plt.legend()
    plt.savefig("static/images/" + stock + "-Stock.jpeg")
    stock_image_1 = stock + "-Stock.jpeg"

    # Calculating the Period SMA
    stock_data['SMA'] = stock_data['Close'].rolling(window = period, min_periods = 1).mean()

    #Plotting Close Price, Period SMA, & Data
    plt.figure(figsize = (20,10))
    stock_data['Close'].plot(color = 'k', label= 'Close Price', linewidth = 2) 
    stock_data['SMA'].plot(color = 'rebeccapurple',label = str(period) + "-Day SMA", linewidth = 2) 
    plt.ylabel('Price (USD)')
    plt.xlabel('Date')
    plt.legend()
    plt.grid()
    plt.savefig("static/images/" + stock + "-" + str(period) + "-Day-SMA.jpeg")
    stock_image_2 = stock + "-" + str(period) + "-Day-SMA.jpeg"

    #Calculating the Exponential Moving Average
    stock_data['EMA'] = stock_data['Close'].ewm(min_periods = EMA_minimum_periods, alpha = smoothing_factor).mean()

    #Plotting the EMA, and Close Price
    plt.figure(figsize = (20, 10))
    stock_data['Close'].plot(color = 'black', label = 'Close Price', linewidth = 2)
    stock_data['EMA'].plot(color = 'orange', label = str(EMA_minimum_periods) + " Day EMA", linewidth = 2)
    plt.ylabel('Price (USD)')
    plt.xlabel('Date')
    plt.legend()
    plt.grid()
    plt.savefig('static/images/' + stock + '-' + str(EMA_minimum_periods) + '-Day-EMA.jpeg')
    stock_image_3 = stock + '-' + str(EMA_minimum_periods) + '-Day-EMA.jpeg'
    

    #Calculating Bollinger Bands
    stock_data['TP'] = (stock_data['Close'] + stock_data['Low'] + stock_data['High'])/3
    stock_data['std'] = stock_data['TP'].rolling(period).std(ddof=0)
    stock_data['MA-TP'] = stock_data['TP'].rolling(period).mean()
    stock_data['BLB'] = stock_data['MA-TP'] - SDs*stock_data['std']
    stock_data['BUB'] = stock_data['MA-TP'] + SDs*stock_data['std']

    #Plotting Close Price, SMA, & Data
    plt.figure(figsize = (20, 10))
    stock_data['BLB'].plot(color = "darkgreen", label = 'BLB', linewidth = 2)
    stock_data['BUB'].plot(color = "darkred", label = 'BUB', linewidth = 2)
    stock_data['Close'].plot(color = "black", label = 'Close Price', linewidth = 2)
    plt.fill_between(stock_data.index, stock_data['BUB'], stock_data['BLB'], facecolor='peru', alpha=0.1)
    plt.ylabel('Price (USD)')
    plt.xlabel('Date')
    plt.legend()
    plt.grid()
    plt.savefig("static/images/" + stock + "-BB.jpeg")
    stock_image_4 = stock + "-BB.jpeg"

    #Plotting Buy and Sell Points
    plt.figure(figsize = (20, 10))
    stock_data['BLB'].plot(color = "darkgreen", label = 'BLB', linewidth = 2)
    stock_data['BUB'].plot(color = "darkred", label = 'BUB', linewidth = 2)
    stock_data['SMA'].plot(color = 'rebeccapurple',label = str(period) + "-Day SMA", linewidth = 2) 
    stock_data['Close'].plot(color = "black", label = 'Close Price', linewidth = 2)


    plt.fill_between(stock_data.index, stock_data['BUB'], stock_data['BLB'], facecolor='peru', alpha=0.1)

    # 0 --> holding, -1 --> sell, 1 --> buy

    holding = True
    totalProfitPerShare = 0.0
    lastBuy = stock_data.iat[0, 0]
    lastSell = 0

    first = True
    for index, row in stock_data.iterrows():
        if first:
            plt.plot(index, row["Close"], marker='^', markersize = 13, color='g')
            first = False
        if row["Close"] >= row["BUB"] and holding == True:
            holding = False
            lastSell = row["Close"]
            totalProfitPerShare += lastSell - lastBuy
            plt.plot(index, row["Close"], marker='v', markersize = 13, color='r')       
            # print("sold at " + str(row["Close"]))

        elif row["Close"] <= row["BLB"] and holding == False:
            holding = True
            lastBuy = row["Close"]
            # print("bought at " + str(row["Close"]))
            plt.plot(index, row["Close"], marker='^', markersize = 13, color='g')       

    if holding:
        lastSell = stock_data.iat[-1,0]
        # print(lastSell)
        totalProfitPerShare += lastSell - lastBuy
    plt.ylabel('Price (USD)')
    plt.xlabel('Date')
    plt.legend()
    plt.grid()
    plt.savefig("static/images/" + stock + "-BuySell.jpeg")
    stock_image_5 = stock + "-BuySell.jpeg"
    # figure = plt.figure()
    # mpld3_image = mpld3.fig_to_html(figure, no_extras=False, template_type = "simple")
    # print(mpld3_image)

    return stock_image_1, stock_image_2, stock_image_3, stock_image_4, stock_image_5, totalProfitPerShare, company_name, company_website

# Delete uploaded images from folder
def remove_images():
    for file in os.listdir('static/images'):
        if file.endswith('.jpeg'):
            os.remove(r"C:/Users/oluwa/OneDrive/Desktop/Citadel Externship/FinalProject/static/images/" + file)