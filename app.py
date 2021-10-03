from flask import Flask, render_template, request
from main import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def respond():
    finals = []
    number = 0
    if request.method == "POST":
        number = request.form.get("number")
        finals = arbitrage(number)
    return render_template('index.html', finals=finals, i = number)

if __name__ == '__main__':
    app.run()