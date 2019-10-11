from flask import Flask,g , render_template, request, session, redirect, url_for, flash
from flask_mail import Message, Mail
from flask_security import recoverable
import sqlite3
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, URLSafeTimedSerializer, SignatureExpired
import sqlite3
import os
import datetime
import smtplib
from Controllers.TokenHandler import TokenHandler

class EmailHandler:

	def sendConfirmationEmail(email, database, secretkey, mail, url):
		#build database to access it 
		db = database.build_db('database1.db')
		cursor = db.cursor()
		sessionUser = session['user']
		userName = sessionUser.get('userName')
		#generate token
		token = TokenHandler.setTokenForPasswordRecovery(1800, userName, secretkey)
		msg = Message('Password Reset Recovery', sender = '2greeks1italian@gmail.com', recipients=[email])
		msg.body = url_for(url, token = token, _external=True)
		#send message
		try:
			mail.send(msg)
		except smtplib.SMTPRecipientsRefused:
			return redirect(url_for('index'))
		#take user to login page
		return None

	def sendPasswordRecoveryEmail(email, database, secretkey, mail):
		#build database to access it 
		db = database.build_db('database1.db')
		cursor = db.cursor()
		userName = database.selectFromTable(cursor, 'User', 'UserName', 'Email', email)
		#generate token
		token = TokenHandler.setTokenForPasswordRecovery(1800, userName, secretkey)
		msg = Message('Password Reset Recovery', sender = '2greeks1italian@gmail.com', recipients=[email])
		msg.body = url_for('checkTokenInUrl', token = token, _external=True)
		try:
			mail.send(msg)
		except smtplib.SMTPRecipientsRefused:
			return redirect(url_for('index'))
		#take user to login page
		return None