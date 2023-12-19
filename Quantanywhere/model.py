#import dataframes
import os
import warnings
import requests
import numpy as np
import pandas as pd
import yfinance as yf
import empyrical
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

warnings.filterwarnings("ignore")
plt.switch_backend('agg')
plt.style.use('fivethirtyeight')
plt.rcParams["font.family"] = "monospace"
plt.rcParams["axes.grid"] = False
plt.rcParams['font.size'] = 20

def stock_info(stock, period, EMA_minimum_periods, smoothing_factor, SDs, startDate, endDate):
    plt.figure(figsize = (20, 10))
    # Getting the data TSLA
    stock_data = yf.download(stock, startDate, endDate)
    initial_stock_price = stock_data[["Close"]].iloc[0, 0]
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
    signals = []
    lastSell = 0
    first = True
    for index, row in stock_data.iterrows():
        if first:
            plt.plot(index, row["Close"], marker='^', markersize = 13, color='g')
            first = False
            signals.append(1)
        elif row["Close"] >= row["BUB"] and holding == True:
            holding = False
            lastSell = row["Close"]
            totalProfitPerShare += lastSell - lastBuy
            plt.plot(index, row["Close"], marker='v', markersize = 13, color='r')       
            # print("sold at " + str(row["Close"]))
            signals.append(-1)
        elif row["Close"] <= row["BLB"] and holding == False:
            holding = True
            lastBuy = row["Close"]
            # print("bought at " + str(row["Close"]))
            plt.plot(index, row["Close"], marker='^', markersize = 13, color='g')   
            signals.append(1) 
        else:
            signals.append(0)  

    if holding:
        lastSell = stock_data.iat[-1,0]
        # print(lastSell)
        totalProfitPerShare += lastSell - lastBuy
    plt.ylabel('Price (USD)')
    plt.xlabel('Date')
    plt.legend()
    plt.savefig("static/images/" + stock + "-BuySell.jpeg")
    stock_image_5 = stock + "-BuySell.jpeg"
    return stock_image_1, stock_image_2, stock_image_3, stock_image_4, stock_image_5, initial_stock_price, totalProfitPerShare, company_name, company_website, signals

class Backtester():
    def __init__(self):
        self.start_amount = 1

    def set_info(self, initial_investment = 1, stock_name = "SPY", start_date = "2020-01-01", end_date = "2023-08-01", signals = None):
        if not signals: signals = []
        self.data = yf.download(stock_name, start_date, end_date)[["Close"]]
        self.start_amount = initial_investment
        self.stock_name = stock_name
        self.data["Signal"] = signals

    def getBacktestData(self):
        # Buy and Sell logic used to reinvest portfolio for every trade
        arr_label = self.data[["Signal"]].values
        idx_start = 0
        idx_end = (len(self.data))
        arr_raw = self.data[["Close"]]
        arr_raw = arr_raw.values.ravel().tolist()
        arr_label = arr_label[idx_start:idx_end+1] # output labels
        arr_holding_status =[]
        arr_balance_GT = []
        arr_ratio = [1]
        arr_balance = []
        total_amount = self.start_amount
        buy_status = 0
        total_shares = 0
        idx_start = 0
        share_init_GT = total_amount/arr_raw[idx_start]
        arr_label_actual = []

        for k in range(idx_start, len(arr_label)):
            action_flag = arr_label[k]
            price = arr_raw[k]

            if action_flag == 1: # Buy logic
                if buy_status == 0:
                    total_shares = total_amount / price
                buy_status = 1 # assign to buy
            if action_flag == -1: # Sell logic
                if total_shares != 0:
                    total_amount = total_shares * price
                total_shares = 0
                buy_status = 0

            if buy_status == 1: # actual buy
                arr_balance.append(total_shares * price)
                arr_holding_status.append(1)
                if len(arr_holding_status)>=2:
                    if arr_holding_status[-1]==1 and arr_holding_status[-2]==0:
                        arr_label_actual.append(1) # Actual buy
                    else:
                        arr_label_actual.append(0) # No need to buy again
                else:
                    arr_label_actual.append(1) # At very beginning, length smaller than 2
            else: # actual wait
                arr_balance.append(total_amount)
                arr_holding_status.append(0)
                if len(arr_holding_status)>=2:
                    if arr_holding_status[-1]==0 and arr_holding_status[-2]==1:
                        arr_label_actual.append(-1) # Actual sell
                    else:
                        arr_label_actual.append(0) # No need to sell again
                else:
                    arr_label_actual.append(0) # At very beginning, length smaller than 2
            arr_balance_GT.append(share_init_GT * price)
            if k!=idx_start:
                arr_ratio.append(arr_balance[-1]/arr_balance[0])

        arr_ratio = np.array(arr_ratio)
        arr_show = arr_ratio*arr_raw[0]

        buy_hold, sentiment_trade = self.data["Close"], self.data[["Close"]]
        sentiment_trade.drop(columns = ["Close"], inplace = True)
        sentiment_trade["Price"] = arr_show
        self.buy_hold_data, self.sentiment_trade_data = buy_hold, sentiment_trade
        
    def backtest_graphs(self):
        plt.xticks(rotation = 45)
        plt.plot(self.buy_hold_data, label = "Buy & Hold", linewidth = 2, color = "black")
        plt.plot(self.sentiment_trade_data, label = "Trading With Strategy", linewidth = 2, color = "blue")
        plt.xlabel("Date")
        plt.ylabel("Price in USD")
        plt.title(f"Returns For {self.stock_name}")
        plt.legend()

        stock_buysellgraph = str(self.stock_name) + "-TradingResults.jpeg"
        plt.savefig("static/images/" + stock_buysellgraph)
        return stock_buysellgraph
    
    def backtest_results(self):
        # Assuming you have a DataFrame 'df' with daily returns for your portfolio and the risk-free rate
        df = pd.DataFrame()
        df["portfolio"] = self.data[["Close"]].pct_change().dropna()
        sharpe = round(empyrical.sharpe_ratio(df['portfolio']), 3)
        mdd = str(round((empyrical.max_drawdown(df['portfolio']) * 100), 2)) + "%"
        print("Sharpe From Empyrical: ", sharpe)
        print("Max Drawdown:", mdd, "%")
        return sharpe, mdd

# Delete uploaded images from folder
def remove_images():
    for file in os.listdir('static/images'):
        if file.endswith('.jpeg'):
            os.remove(r"C:/Users/oluwa/OneDrive/Desktop/Citadel Externship/Quantanywhere/static/images/" + file)


def send_email(subject = "QuantAnywhere Feedback", phone_number = 1, university = "No School", feedback = ""):
    token="GoGenerateAnApiToken"
    sender = "Quant Anywhere"
    msg_content = "University" + university + feedback
    recipients = [862_224_0924]

    payload = {
        "sender": sender,
        "message": msg_content,
        "recipients": [
            {"msisdn": recipient_number}
            for recipient_number in recipients
        ],
    }
    resp = requests.post(
        "https://gatewayapi.com/rest/mtsms",
        json=payload,
        auth=(token, ""),
    )
    print("Worked")
    resp.raise_for_status()
