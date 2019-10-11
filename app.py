from flask import Flask,g , render_template, request, session, redirect, url_for, flash
from flask_mail import Message, Mail
#from flask_security import recoverable
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from Classes.User import User
from Classes.Posts import Posts
#import Classes.Posts
#import Classes.User

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, URLSafeTimedSerializer, SignatureExpired
import sqlite3
import os
import datetime
import smtplib

#import controller classes
from Controllers.Dbcontroller import Dbcontroller
from StaticClasses.EmailHandler import EmailHandler
from StaticClasses.XSSProtection import XSSProtection
from StaticClasses.InputValidator import InputValidator
from StaticClasses.TokenHandler import TokenHandler
from StaticClasses.SQLInjectionProtection import SQLInjectionProtection
app = Flask(__name__)

app.config.from_object(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

#set up mail server config
app.config['MAIL_SERVER'] = 'imap.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True

#NOT SECURE - for purposes of coursework and pen test group
app.config['MAIL_USERNAME'] = "2greeks1italian@gmail.com"
app.config['MAIL_PASSWORD'] = "asecurepasswordladz1"
app.config['SECRET_KEY'] = '/x95/xfa/x10/xcd2u/x07/xd1/x7fxe8/xf8m^/x83/x87/xe0T/x01R$/xac/xfbxa1/r'

mail = Mail(app)

#set up session
app.permanent_session_lifetime = datetime.timedelta(1800) #lifetime of session

newUser = None
newUser = User('bong','sarikas','nsarikas','email','password',0)

database = Dbcontroller('database1.db')

@app.route('/')
def index():
	db = database.build_db('database1.db')
	cursor = db.cursor()
	#check if user is logged in
	if 'user' in session:
		#take user to profile
		return redirect(url_for('newsfeed'))
	else:
		#render log in page
		return render_template('index.html', user=newUser,)

@app.route("/register", methods=['POST'])
def register():
	if request.method == "POST":
		#build database to access it
		db = database.build_db('database1.db')
		cursor = db.cursor()
		username = request.form['username']
		usernameIsUnique = InputValidator.isUnique(username, database)
		password1 = request.form['password1']
		password2 = request.form['password2']

		#executes registration if passwords are matching, the password has met requirements, the username is unique and not empty
		if password1 == password2 and len(password1)>9 and usernameIsUnique == True and len(username) > 0:
			#get user input
			firstName = (request.form['firstname'])
			surName = (request.form['surname'])
			userName = (request.form['username'])
			password = (request.form['password1'])
			email = (request.form['email'])			
			#validate user input
			validatedFirstName = XSSProtection.xssSanitisation(firstName)
			validatedSurName = XSSProtection.xssSanitisation(surName)
			validatedUserName = XSSProtection.xssSanitisation(userName)
			validatedPassword = XSSProtection.xssSanitisation(password)
			validatedEmail = XSSProtection.xssSanitisation(email)
			#hash user password
			hashedValidatedPassword = generate_password_hash(validatedPassword)
			#set user inputs			
			newUser.set_firstName(validatedFirstName)
			newUser.set_surName(validatedSurName)
			newUser.set_userName(validatedUserName)
			newUser.set_password(hashedValidatedPassword)
			newUser.set_email(validatedEmail)
			#place user and csrf token in session
			session['user'] = vars(newUser)
			session['postsCounter'] = 0
			session['startTime'] = datetime.datetime.now()
			session['token'] = TokenHandler.setCSRFtoken(1800, app.config['SECRET_KEY'])
			#user must confirm email before they are commited to DB
			EmailHandler.sendConfirmationEmail(email, database, app.config['SECRET_KEY'], mail, 'confirmEmail')
			return render_template('index.html', error = 'Confirmation link sent to your email')		
		#if passwords aren't the same or password is less than 10 characters, show error
		if (password1 != password2) or len(password1)<10:
			return render_template('index.html', error = "Passwords requirements not met")
		else:
			return render_template('index.html', error = "Invalid Username or Password")

#executed when login submit is pressed
@app.route("/login", methods=['POST'])
def login():
	if request.method == 'POST':
		#require email and password to log in
		email = request.form['logEmail']
		password = request.form['logPassword']
		#input validation
		validatedEmail = XSSProtection.xssSanitisation(email)
		validatedPassword = XSSProtection.xssSanitisation(password)
		#build database to access it
		db = database.build_db('database1.db')
		cursor = db.cursor()
		
		#if login is successful
		log = database.log_in(validatedEmail,validatedPassword,cursor,newUser)
		if log == True:
			#place user in session and set CSRF token in session
			#set isAdmin value of user
			newUser.set_isAdmin(int(database.selectFromTable(cursor, 'User', 'isAdmin', 'UserName', newUser.get_userName())))
			session['user'] = vars(newUser)
			session['postsCounter'] = 0
			session['startTime'] = datetime.datetime.now()
			session['token'] = TokenHandler.setCSRFtoken(1800, app.config['SECRET_KEY'])
			#redirect user to newsfeed
			return redirect(url_for('newsfeed'))
			flash('You logged in successfully')
		else:
			#reload page
			error = "Invalid Username or Password"
			return render_template('index.html', error = error)

#logic for newsfeed page
@app.route('/newsfeed')
def newsfeed():
	#build database to access it
	db = database.build_db('database1.db')
	cursor = db.cursor()
	#check if user is logged in
	if 'user' in session:
		#load posts from database
		postings = database.getPostList(cursor)
		sessionToken = session['token']
		#display page with posts and no message
		return render_template('home.html', postings=postings, message = '', token = sessionToken) 
	else:
		#send user to login page
		return redirect(url_for('index'))

#executes when ban submit button it pressed
@app.route('/banUser', methods = ['POST'])
def banUser():
	if request.method == "POST":
		#build databse to access it
		db = database.build_db('database1.db')
		cursor = db.cursor()
		#gets username to be banned from admin's input
		bannedUserName = request.form['user']
		#checks that the admin has full privileges
		user = session['user']
		isAdmin = user.get('isAdmin')
		if isAdmin == True:
			#bans the user in the database - effective immediately
			database.ban_user(bannedUserName, 1,cursor)
			return redirect(url_for('profile'))
	else:
		return redirect(url_for('profile'))

#executes when ban submit button it pressed
@app.route('/unbanUser', methods = ['POST'])
def unbanUser():
	if request.method == "POST":
		#build databse to access it
		db = database.build_db('database1.db')
		cursor = db.cursor()
		#gets username to be banned from admin's input
		bannedUserName = request.form['user']
		#checks that the admin has full privileges
		user = session['user']
		isAdmin = user.get('isAdmin')
		if isAdmin == True:
			#bans the user in the database - effective immediately
			database.ban_user(bannedUserName, 0,cursor)
			return redirect(url_for('profile'))
	else:
		return redirect(url_for('profile'))

#executes when log out button is pressed
@app.route('/logout')
def logout():
	#clears user object and session
	newUser = None
	session.clear()
	#renders login page
	return redirect(url_for('index'))

#executed when profile loaded
@app.route('/profile', methods=['GET'])
def profile(): 
	if request.method == "GET":
		#build database to access it
		db = database.build_db('database1.db')
		cursor = db.cursor()
		#check if user is logged in
		if 'user' in session:
			#access user stored in session
			user = session['user']
			#render the profile with no message
			userToken = session['token']
			return render_template('profile.html', user = user, message = '', token = userToken)
		else:
			#take user to login page
			return redirect(url_for('index'))

#sent to user in email to confirm email address
@app.route("/confirmEmail/<token>", methods = ['GET','POST'])
def confirmEmail(token):
	#build database to access it
	db = database.build_db('database1.db')
	cursor = db.cursor()
	sessionUser = session['user']
	sessionUsername = sessionUser.get('userName')
	tokenUsername = TokenHandler.verifyTokenForPasswordRecovery(token, database, app.config['SECRET_KEY']) #same method as used for password recovery
	print('token retrieved')
	if tokenUsername == sessionUsername:
		print('token verified')
		try:
			##create user in database
			tempfName = sessionUser.get('firstName')
			tempsName = sessionUser.get('secondName')
			tempuName = sessionUser.get('userName')
			temppWord = sessionUser.get('password')
			tempEmail = sessionUser.get('email')
			database.registration(tempfName,tempsName,tempuName,temppWord,tempEmail,cursor)
		except sqlite3.IntegrityError:
			return redirect(url_for('logout'))
	#log user out so they can log back in with their credentials
	return redirect(url_for('logout'))

#route when user attempts to change email on profile page
@app.route("/changeEmailRequest", methods = ['POST'])
def changeEmailRequest():
	user = session['user']
	username = user.get('userName')
	if request.method == "POST":
		#get email from form		
		newEmail = request.form['email']
		#input validation
		validatedNewEmail = XSSProtection.xssSanitisation(newEmail)
		newUser.email = newEmail
		session['user'] = vars(newUser)
		EmailHandler.sendConfirmationEmail(newEmail, database, app.config['SECRET_KEY'], mail, 'changeEmail')
	return redirect(url_for('profile'))


#sent to user in email to confirm new email address
@app.route("/changeEmail/<token>")
def changeEmail(token):
	#build database to access it
	db = database.build_db('database1.db')
	cursor = db.cursor()
	sessionUser = session['user']
	sessionUsername = sessionUser.get('userName')
	#verify token in url with users token
	tokenUsername = TokenHandler.verifyTokenForPasswordRecovery(token, database, app.config['SECRET_KEY']) #same method as used for password recovery
	print('token retrieved')
	if tokenUsername == sessionUsername:
		print('token verified')
		try:
			#update the users email
			user = session['user']
			email = user.get('email')
			username = user.get('userName')
			db = database.build_db('database.db')
			cursor = db.cursor()
			database.updateTable(cursor, 'User', 'Email', email, 'UserName', username)
		except sqlite3.IntegrityError:
			#take user to profile
			return redirect(url_for('profile'))
	return redirect(url_for('profile'))

#executes when the changed password submit button is pressed
@app.route('/changePassword', methods = ['POST'])
def changePassword():
	#CSRF Protection - only changes password if tokens match
	formToken = request.form['csrfToken']
	userToken = session['token']
	if formToken == userToken:
		#build database to access it
		db = database.build_db('database1.db')
		cursor = db.cursor()
		#get username stored in session
		user = session['user']
		username = user.get('userName')
		if request.method == "POST":
			#get user-entered form data
			currentPassword = request.form['password']
			newPassword1 = request.form['newPassword1']
			newPassword2 = request.form['newPassword2']		
			#input validation
			validatedCurrentPassword = XSSProtection.xssSanitisation(currentPassword)
			validatedNewPassword1 = XSSProtection.xssSanitisation(newPassword1)
			validatedNewPassword2 = XSSProtection.xssSanitisation(newPassword2)
			#get email from current user
			currentEmail = user.get('email')
			#check validity of information
			storedPassword = database.selectFromTable(cursor, 'User', 'Password', 'UserName', username)
			#executes if the validated passwords are matching, the password has met requirements and the validated password matches the stored password
			if validatedNewPassword1 == validatedNewPassword2 and len(newPassword1)>9 and (check_password_hash(storedPassword, validatedCurrentPassword) == True):
				#change password
				hashedValidatedNewPassword = generate_password_hash(validatedNewPassword1)
				database.updateTable(cursor, 'User', 'Password', hashedValidatedNewPassword, 'UserName', username)
				#render user profile again
				return render_template('profile.html', user = user, message = 'Password Changed', token = userToken)
			elif check_password_hash(storedPassword, validatedCurrentPassword) == False:
				return render_template('profile.html', user = user, message = 'Invalid Credentials', token = userToken)
			#if the passwords do no match or is less than 10 characters, display error message
			elif validatedNewPassword1 != validatedNewPassword2 or len(newPassword1)<10:
				return render_template('profile.html', user = user, message = 'Password requirements not met', token = userToken)
			else:
				#render user profile with error message
				return render_template('profile.html', user = user, message = 'Invalid Credentials', token = userToken)
	else:
		return redirect(url_for('profile'))

@app.route("/forgotPassword", methods = ['GET','POST'])
def forgotPassword():
	#no curent active user
	if 'user' not in session:
		email = request.form['resetPasswordEmail']
		EmailHandler.sendPasswordRecoveryEmail(email, database, app.config['SECRET_KEY'], mail)
		return render_template('index.html')
	else:
		return redirect(url_for('newsfeed'))

#link sent to user in an email to reset their password
@app.route("/resetPassword/<token>", methods=['GET','POST'])
def checkTokenInUrl(token):
	#user mest be logged out to reach this page
	if 'user' not in session:
		userName = TokenHandler.verifyTokenForPasswordRecovery(token, database, app.config['SECRET_KEY'])
		#token expired - return to forgot password request page
		if userName is None:
			return redirect(url_for('index'))
		else:
			#store username from token in a temporary session for the password reset
			session['userName'] = userName
			return render_template('reset_password.html')
	else:
		return redirect(url_for('newsfeed'))

#page where the user sets a new password if they forgot the old one
@app.route("/resetPassword", methods=['POST'])
def resetPassword():
	#build database to access it
	db = database.build_db('database1.db')
	cursor = db.cursor() 	
	#access username from token stored in session
	userName = session['userName']
	#check both passwords match
	password1 = request.form['password1']
	password2 = request.form['password2']
	#input validation
	validatedPassword1 = XSSProtection.xssSanitisation(password1)
	validatedPassword2 = XSSProtection.xssSanitisation(password2)
	if validatedPassword1 == validatedPassword2 and len(password1)>9:
		#reset the password and return user to the log in page
		hashedValidatedNewPassword = generate_password_hash(validatedPassword1)
		database.updateTable(cursor, 'User', 'Password', hashedValidatedNewPassword, 'UserName', userName)
		#clear the temporary session used to hold the username
		session.clear()
		return redirect(url_for('index'))
	else:
		error = 'Password requirements not met'
		return render_template('reset_password.html', error=error)

@app.route("/writePost", methods=['POST'])
def writePost():
	#CSRF Protection - only post if tokens match
	formToken = request.form['csrfToken']
	userToken = session['token']
	if formToken == userToken:
		if request.method == "POST":
			#build database to access it
			db = database.build_db('database1.db')
			cursor = db.cursor()
			#get comment type by the user into the form
			content = request.form['content']
			#input validation
			validatedContent = XSSProtection.xssSanitisation(content)
			#get up to date posts
			postings = database.getPostList(cursor)
			#get username from session
			user = session['user']
			userName = user.get('userName')
			#gets the isBanned value from database to ensure all information is up to date
			#does not use the user object as this is only updated on login
			isBanned = int(database.selectFromTable(cursor, 'User', 'isBanned', 'UserName',userName))
			postComplete = False
			postsCounter = session['postsCounter']
			startTime = session['startTime']
			if isBanned == 0:
				#Spam Filter - Bans user if they post more than 100 times in 10 seconds - most likely a bot
				currentTime = datetime.datetime.now()
				timer = currentTime.second - startTime.second
				if timer > 10:
					startTime = datetime.datetime.now()
					postsCounter = 0
				if postsCounter >= 100:
					database.ban_user(userName, cursor)
					return redirect(url_for('index'))
				postComplete = database.makePost(validatedContent, userName, cursor)
			if postComplete == True:
				#update post list
				postings = database.getPostList(cursor)
				return redirect(url_for('newsfeed'))
			else:
				#return home template notifying the user than they have been banned
				return render_template('home.html', user=newUser, postings=postings, message = 'YOU HAVE BEEN BANNED!', token = userToken) 
	else:
		return redirect(url_for("index"))

if __name__ == "__main__":
	app.run(debug=False)
	#in future when certificate acquired run app in https mode
	#app.run(ssl_context='adhoc')