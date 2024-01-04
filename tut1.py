import flask
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/about')
def about():
    name ='leena'
    return render_template("about.html",ian =name)

@app.route('/bootstrap')
def boot():
    return render_template("bootstrap.html")

app.run(debug=True)

