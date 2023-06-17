from flask import Flask
from flask import render_template
from flask import request, jsonify
from flask import redirect
from model import stock_info
from model import remove_images
import os


app = Flask(__name__)

####################
# ROUTES
####################

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     data = request.json
#     user_input = data['input']
    
#     # Make a request to the OpenAI API
#     response = openai.Completion.create(
#         engine='text-davinci-003',  # Choose the appropriate GPT model
#         prompt=user_input,
#         max_tokens=50  # Adjust the desired length of the response
#     )
    
#     return jsonify({'response': response['choices'][0]['text'].strip()})

@app.route('/')
@app.route('/index', methods = ["GET"])
def index():
    remove_images()
    return render_template('index.html')

@app.route('/contact', methods = ["GET"])
def contact():
    return render_template('contact.html')

@app.route('/thankyou', methods = ["POST"])
def thanks():
    return render_template('thankyou.html')

@app.route('/graphs', methods = ["GET", "POST"])
def graphs():
    if request.method == 'GET':
        return render_template('graphs.html')
    else:
        period = int(request.form['period'])
        SDs = float(request.form['SDs'])
        stock = str(request.form['stock']).upper()
        EMA_period = int(request.form['EMA_period'])
        alpha = float(request.form['EMA_alpha'])
        startDate = request.form['startDate']
        endDate = request.form['endDate']

        image_1, image_2, image_3, image_4, image_5, profitPerShare, stock_name, website = stock_info(stock, period, EMA_period, alpha, SDs, startDate, endDate)
        user = {
            "stock": stock,
            "period": period,
            "SDs": SDs,
            "EMA_period": EMA_period,
            'EMA_alpha': alpha,
            "startDate": startDate,
            "endDate": endDate,
            "image_1": image_1,
            "image_2": image_2,
            "image_3": image_3,
            "image_4": image_4,
            "image_5": image_5,
            "profitPerShare": profitPerShare,
            "company_name": stock_name,
            "company_website": website
        }        
        return render_template('graphs.html', user = user)

@app.route('/results', methods = ["GET", "POST"])
def results():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        period = int(request.form['period'])
        SDs = float(request.form['SDs'])
        stock = str(request.form['stock']).upper()
        startDate = request.form['startDate']
        endDate = request.form['endDate']

        numShares = int(request.form['numShares'])
        image_5 = request.form['image_5']
        profitPerShare = float(request.form['profitPerShare'])
        profitPerShare = round(profitPerShare, 2)
        profitPerShareStr = ('{:,}'.format(profitPerShare))
        totalProfit = round(float(numShares * profitPerShare), 2)
        totalProfit = ('{:,}'.format(totalProfit))
        numShares = ('{:,}'.format(numShares))
        if numShares == "0":
            totalProfit = "0"
        user = {
            "period": period,
            "SDs": SDs,
            "stock": stock,
            "startDate": startDate,
            "endDate": endDate,
            "image_5": image_5,
            "profitPerShare": profitPerShareStr,
            "numShares": numShares,
            "totalProfit": totalProfit
        }        
        return render_template('results.html', user = user)

@app.route('/strats', methods = ["GET", "POST"])
def strats():
    return render_template('strats.html')