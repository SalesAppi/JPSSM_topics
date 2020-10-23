from app import app
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
# from app import model as predict

import gensim
import re

from gensim.models import LdaModel
from gensim.test.utils import datapath
from gensim import corpora, models
from gensim.corpora import Dictionary

from re import sub
import os
import string
import codecs

import nltk

from nltk.tokenize import RegexpTokenizer
from nltk import stem
from nltk.stem import WordNetLemmatizer

def remove_shorts (words):
    words = re.sub(r'\b\w{1,3}\b', '', words)
    return words

def remove_special_characters(words, remove_digits=False):
    pattern = r'[^a-zA-z0-9\s]' if not remove_digits else r'[^a-zA-z\s]'
    words = re.sub(pattern, '', words)
    return words

def normalize(words):
    words = remove_shorts(words)
    words = remove_special_characters(words, remove_digits=True)
    return words

def create_stopwords(path):
    stop_words = []
    for w in open(path, "r",encoding="utf-8"):
        w = w.replace('\n','')
        if len(w) > 0:
             stop_words.append(w)
    return stop_words

absFilePath = os.path.abspath(__file__)                # Absolute Path of the module

fileDir = os.path.dirname(os.path.abspath(__file__))   # Directory of the Module

parentDir = os.path.dirname(fileDir)                   # Directory of the Module directory

modelPath = os.path.join(fileDir, 'model')             # Get the directory for model

filePath = os.path.join(fileDir, 'upload')              # Directory of the test file

swPath = os.path.join(fileDir, 'files')   

temp_file = datapath((os.path.join(modelPath, 'LDAmodel_K17')))
lda_model = LdaModel.load(datapath(temp_file))

# create stop_words
temp_file = datapath((os.path.join(swPath, 'JPSSM_project.txt')))
stop_words = create_stopwords(temp_file)

# load dictionary
original = Dictionary.load((os.path.join(modelPath, 'LDAmodel_K17.id2word')))

#app = Flask(__name__)

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

@app.route("/text-submit/", methods=["GET", "POST"])
def text_submit():
    if request.method=='GET':
        return render_template('/text_submit.html')
    elif request.method=='POST':
        user_txt = request.form.get('user_txt')
        print(user_txt)
        
        test_file = user_txt

        # prepare the Text
        # clean up text: rem white space, new line marks, blank lines
        body_text = test_file.strip().replace('  ', ' ')
        body_text = body_text.replace('\n', ' ').replace('\r', '')

            # delete digits
        body_text = sub(pattern=r"\d", repl=r" ", string=body_text)

            # remove punctuation - updated
        translator = str.maketrans(' ',' ', string.punctuation)
        body_text = body_text.translate(translator)
        body_text = os.linesep.join([s for s in body_text.splitlines() if s])


        # further processing
        tokenizer = RegexpTokenizer(r'\w+')
        lemmatizer = stem.WordNetLemmatizer()
        test_text=[]
        raw = body_text.lower()
        raw = normalize(raw)
        tokens = tokenizer.tokenize(raw)
        stopped_tokens = [i for i in tokens if not i in stop_words]
        lemmatized_tokens = [lemmatizer.lemmatize(i) for i in stopped_tokens]
        test_text.extend(lemmatized_tokens)


        doc = raw
        doc = doc.lower()
        doc = doc.split()
        vec_bow = original.doc2bow(doc)
        vec_lda = lda_model[vec_bow]
        # return list of topics
     #   print(vec_lda)
        result=dict(vec_lda)

        from collections import OrderedDict
        result = OrderedDict(sorted(result.items(), key=lambda x: x[1], reverse = True))

        dane=[]
        for x in result.values():
  #          print ("{:.3f}".format(x))
            dane.append("{:.2f}".format(x))

 #       def key_remapper(dict: dict):
 #           return {remap_dictionary.get(k, v): v for k, v in dict.items()}

        def map_fields(init_dict, map_dict, res_dict=None):
            res_dict = res_dict or {}
            for k, v in init_dict.items():
                if isinstance(v, dict):
                    v = map_fields(v, map_dict)
                if k in map_dict.keys():
                    k = str(map_dict[k])
                res_dict[k] = v
    
            return res_dict

        topic_names = {0:"Econometric models of performance",1:"Commitment-Trust in Sales",2:"Diversity and inclusion in sales",3:"Sales technology & systems 1.0",4:"Compensation / Bonus",5:"Customer orientation",6:"Scales in sales research",7:"Sales technology & systems 2.0",8:"Research methods",9:"Salesperson interpersonal communication",10:"Sales teams",11:"Salespeople turnover",12:"International sales",13:"Salesperson's evaluation and training",14:"Salesperson's success and failure",15:"Buyer-seller relationship", 16:"Leadership and adaptive selling"}
        

        result_dict = map_fields(result, topic_names)


        result = {}
        result = result_dict

    return render_template('text_submit.html', result=result, dane=dane)

@app.route("/result", methods=["GET"])
def result():
    return render_template('text_submit.html', results=result)

if __name__ == '__main__':
    app.run()