from app import app
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = ''
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route("/")
def home():
    return "Welcome page <h1>hello</h1>"

@app.route("/upload-file", methods=["GET", "POST"])
def upload_file():
    return render_template("public/upload_file.html")

@app.route("/text-submit", methods=["GET", "POST"])
def text_submit():
    if request.method=='GET':
        return render_template('text_submit.html')
    elif request.method=='POST':
        user_txt = request.form.get('user_txt')
        print(user_txt)
    return user_txt

if __name__ == '__main__':
    app.run()