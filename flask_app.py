#!/usr/bin/env python
import os
import sys

from flask import *
from io import BytesIO
from PIL import Image, ImageOps
import base64
import urllib

import numpy as np
import scipy.misc
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import os
import tensorflow as tf
import numpy as np
from tensorflow import keras
#from skimage import io
from tensorflow.keras.preprocessing import image


# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
from tensorflow.keras.models import load_model



from flask_mysqldb import *
from flask_mail import Mail, Message

app = Flask(__name__) #Initialize the flask App

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'glovishtech777@gmail.com'
app.config['MAIL_PASSWORD'] = 'sdkfheoiujlrmzpq'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
 
app.secret_key = "phishingwebsite"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'nithya'
app.config['MYSQL_DB'] = 'phishingwebsite'
mysql = MySQL(app)

@app.route('/sendmail',methods=['post'])
def sendmail():
    mailid = request.form['mail']
    print(mailid)
    #get cursor to execute commands
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Check if account exists using MySQL)
    cursor.execute('SELECT * FROM reg WHERE email = %s', (mailid,))
    account = cursor.fetchone()
    if(account):
        password=account['password']
        mail_msg = f'Password for your email ID: {password}'  # Format the message as a string
        try:
            msg = Message(
                'Phishing Website Admin',
                sender='glovishtech777@gmail.com',
                recipients=[mailid]
            )
            msg.body = mail_msg
            mail.send(msg)
            print("Email sent successfully")
            return render_template('forgotpassword.html',msg='Email sent successfully')
        except Exception as e:
            print(f"Failed to send email: {e}")
            return render_template('forgotpassword.html',msg='Failed to send mail')
    else:
        return render_template('forgotpassword.html',msg='Email not registered with us')
 

# Load your trained model
 


@app.route("/")
@app.route("/first")
def first():
	return render_template('first.html')
    
@app.route("/login")
def login():
	return render_template('login.html')    

@app.route('/regaction',methods=['POST'])
def regaction():
    # Output message if something goes wrong...
    msg=""

    uname = request.form['uname']
    pwd = request.form['pwd']
    email = request.form['email']

    #get cursor to execute commands
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Check if account exists using MySQL)
    cursor.execute('SELECT * FROM reg WHERE username = %s', (uname,))
    account = cursor.fetchone()
    # If account exists show error and validation checks
    if account:
        msg = "Username already registered"
        flash("Username already registered")
        return render_template('register.html',msg=msg)
    else:
        cursor.execute('INSERT INTO reg VALUES (%s, %s, %s)', (uname, pwd, email,))
        mysql.connection.commit()
        msg = "Register success"
        flash("Register success")
        return render_template('register.html',msg=msg)
    
@app.route('/loginaction', methods=['POST'])
def loginaction():
    msg=""
    username = request.form['uname']
    password = request.form['pwd']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM reg WHERE username = %s and password = %s', (username,password,))
    account = cursor.fetchone()
    if account:
        msg="login success"
        flash("login success")
        return render_template('index.html', account=account, msg=msg)
    else:
        msg = "Invalid Credentials"
        flash("Invalid Credentials")
        return render_template('login.html', msg=msg)


@app.route("/chart")
def chart():
	return render_template('chart.html')

@app.route("/register")
def register():
	return render_template('register.html')

@app.route("/forgotpassword")
def forgotpassword():
	return render_template('forgotpassword.html')

@app.route("/performance")
def performance():
	return render_template('performance.html')


@app.route("/index",methods=['GET'])
def index():
	return render_template('index.html')


@app.route("/upload", methods=['POST'])
def upload_file():
	print("Hello")
	try:
		img = Image.open(BytesIO(request.files['imagefile'].read())).convert('RGB')
		img = ImageOps.fit(img, (224, 224), Image.ANTIALIAS)
	except:
		error_msg = "Please choose an image file!"
		return render_template('index.html', **locals())

	# Call Function to predict
	args = {'input' : img}
	out_pred, out_prob = predict(args)
	out_prob = out_prob * 100

	print(out_pred, out_prob)
	danger = "danger"
	if out_pred=="You Are Safe, But Do keep precaution":
		danger = "success"
	print(danger)
	img_io = BytesIO()
	img.save(img_io, 'PNG')

	png_output = base64.b64encode(img_io.getvalue())
	processed_file = urllib.parse.quote(png_output)

	return render_template('result.html',**locals())
def predict(args):
	img = np.array(args['input']) / 255.0
	img = np.expand_dims(img, axis = 0)

	model = 'save.h5'
	# Load weights into the new model
	model = load_model(model)

	pred = model.predict(img)


	if np.argmax(pred, axis=1)[0] == 0:
		out_pred = "Result: Brain Tumor  Symptoms: unexplained weight loss, double vision or a loss of vision, increased pressure felt in the back of the head, dizziness and a loss of balance, sudden inability to speak, hearing loss, weakness or numbness that gradually worsens on one side of the body."
	elif np.argmax(pred, axis=1)[0] ==1:
		out_pred = "Result: Normal"
	 
	return out_pred, float(np.max(pred))
 
 

if __name__ == '__main__':
    app.run(debug=True)

