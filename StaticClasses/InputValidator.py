from flask import Flask,g , render_template, request, session, redirect, url_for, flash
from flask_mail import Message, Mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, URLSafeTimedSerializer, SignatureExpired
import sqlite3
import os
import datetime
import smtplib

class InputValidator:

    #checks if a username is unique in the database
    def isUnique(username, database):
        isUnique = False
        db = database.build_db('database1.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM User;")
        result = cursor.fetchall()
        if not result:
            isUnique = True
            return isUnique

        for r in result:
            if r[2] == username:
                isUnique = False
                return isUnique
            if r[2] != username:
                isUnique = True
                return isUnique