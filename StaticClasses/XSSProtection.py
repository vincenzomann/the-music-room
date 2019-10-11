from flask import Flask,g , render_template, request, session, redirect, url_for, flash
from flask_mail import Message, Mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, URLSafeTimedSerializer, SignatureExpired
import sqlite3
import os
import datetime
import smtplib

class XSSProtection:

    def xssSanitisation(input):
        try:
            #encode to utf-8 to disbale us-acii XSS
            inputStr = str(input)
            inputStr = input.encode('utf-8')
            inputStr = str(input)
            if "<" in inputStr:
                #removes tag opening less than sign
                inputStr = inputStr.replace("<", "&lt")
                #allowed harmless tags whitelist
                #<b> tag
                inputStr = inputStr.replace("&ltb>", "<b>")
                inputStr = inputStr.replace("&lt/b>", "</b>")
                #<s> tag
                inputStr = inputStr.replace("&lts>", "<s>")
                inputStr = inputStr.replace("&lt/s>", "</s>")
                #<i> tag
                inputStr = inputStr.replace("&lti>", "<i>")
                inputStr = inputStr.replace("&lt/i>", "</i>")
                #<strong> tag
                inputStr = inputStr.replace("&ltstrong>", "<strong>")
                inputStr = inputStr.replace("&lt/strong>", "</strong>")
            #inputStr.decode('utf-8')
            return inputStr
        except UnicodeDecodeError:
            return redirect(url_for('newsfeed'))