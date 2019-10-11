from flask import Flask,g , render_template, request, session, redirect, url_for, flash
from flask_mail import Message, Mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, URLSafeTimedSerializer, SignatureExpired
import sqlite3
import os
import datetime
import smtplib

class TokenHandler:
        
    def setTokenForPasswordRecovery(lifetimeSec, userName, secretkey):
        #create token with username stored within
        s = Serializer(secretkey, lifetimeSec)
        token = s.dumps({'userName': userName}).decode('utf-8')
        return token

    def setCSRFtoken(lifetimeSec, secretkey):
        user = session['user']
        userName = user.get('userName')
        #creates a token based on username of logged in user
        s = Serializer(secretkey, lifetimeSec)
        token = s.dumps({'userName': userName}).decode('utf-8')
        return token

    def verifyTokenForPasswordRecovery(token, database, secretkey):
        #build database to access it
        db = database.build_db('database1.db')
        cursor = db.cursor()
        #attempt to retrieve the username from the token
        s = Serializer(secretkey)
        userName = ''
        try:
            userName = s.loads(token)['userName']
        except:
            return None
        return userName