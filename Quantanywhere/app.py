from flask import Flask
from flask import render_template
from flask import request, jsonify
from flask import redirect
from model import stock_info
from model import remove_images, Backtester
import os

app = Flask(__name__)
backtester = Backtester()
####################
# ROUTES
####################

@app.route("/")
@app.route("/index", methods = ["GET"])
def index():
    remove_images()
    return render_template("index.html")

@app.route("/contact", methods = ["GET"])
def contact():
    return render_template("contact.html")

@app.route("/thank-you", methods = ["POST"])
def thanks():
    if request.method == "GET":
        return render_template("thank-you.html")
    else:
        email = str(request.form["inputEmail4"])
        phone_number = str(request.form["inputTel"])
        corporation = str(request.form["inputCompany"])
        city = str(request.form["inputCity"])
        state = str(request.form["inputState"])
        zip_code = str(request.form["inputZip"])
        feedback = str(request.form["textInput"])
        user = {
            "email": email,
            "phone_number": phone_number,
            "corporation": corporation,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "feedback": feedback
        }        
        return render_template("thank-you.html", user = user)

@app.route("/graphs", methods = ["GET", "POST"])
def graphs():
    if request.method == "GET":
        return render_template("graphs.html")
    else:
        period = int(request.form["period"])
        SDs = float(request.form["SDs"])
        stock = str(request.form["stock"]).upper()
        EMA_period = int(request.form["EMA_period"])
        alpha = float(request.form["EMA_alpha"])
        startDate = request.form["startDate"]
        endDate = request.form["endDate"]
        try:
            image_1, image_2, image_3, image_4, image_5, initial_share_price, profitPerShare, stock_name, website, signal_array = stock_info(stock, period, EMA_period, alpha, SDs, startDate, endDate)
        except:
            return render_template("index.html")
        backtester.set_info(stock_name = stock, start_date = startDate, end_date = endDate, signals = signal_array)
        user = {
            "stock": stock,
            "period": period,
            "SDs": SDs,
            "EMA_period": EMA_period,
            "EMA_alpha": alpha,
            "startDate": startDate,
            "endDate": endDate,
            "image_1": image_1,
            "image_2": image_2,
            "image_3": image_3,
            "image_4": image_4,
            "image_5": image_5,
            "profitPerShare": profitPerShare,
            "initial_share_price": initial_share_price,
            "company_name": stock_name,
            "company_website": website
        }        
        return render_template("graphs.html", user = user)

@app.route("/results", methods = ["GET", "POST"])
def results():
    if request.method == "GET":
        return render_template("index.html")
    else:
        period = int(request.form["period"])
        SDs = float(request.form["SDs"])
        stock = str(request.form["stock"]).upper()
        startDate = request.form["startDate"]
        endDate = request.form["endDate"]
        initial_investment = int(request.form["start_investment"])
        inital_share_price = float(request.form["initial_share_price"])
        profitPerShare = float(request.form["profitPerShare"])
        profitPerShare = round(profitPerShare, 2)
        backtester.start_amount = initial_investment
        image_5 = request.form["image_5"]
        numShares = ("{:,}".format(round(initial_investment / inital_share_price, 1)))
        profitPerShareStr = ("{:,}".format(profitPerShare))
        totalProfit = round(float(initial_investment * profitPerShare), 2)
        totalProfit = ("{:,}".format(totalProfit))
        initial_investment = ("{:,}".format(initial_investment))
        if initial_investment == initial_investment == "0": totalProfit = "0"
        backtester.getBacktestData()
        backtest_graphname = backtester.backtest_graphs()
        sharpe, mdd = backtester.backtest_results()
        user = {
            "period": period,
            "SDs": SDs,
            "stock": stock,
            "startDate": startDate,
            "endDate": endDate,
            "image_5": image_5,
            "profitPerShare": profitPerShareStr,
            "numShares" : numShares,
            "initial_investment": initial_investment,
            "totalProfit": totalProfit,
            "backtest_graph": backtest_graphname,
            "sharpe_ratio": sharpe, 
            "mdd": mdd
        }        
        return render_template("results.html", user = user)
    
@app.route("/strats", methods = ["GET", "POST"])
def strats():
    return render_template("strats.html")

@app.route("/resources", methods = ["GET", "POST"])
def resources():
    return render_template("resources.html")