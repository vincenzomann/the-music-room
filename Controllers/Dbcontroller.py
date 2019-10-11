from flask import Flask, g, request
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
import datetime
import time
from Classes.User import User
from Classes.Posts import Posts
from StaticClasses.SQLInjectionProtection import SQLInjectionProtection

class Dbcontroller:
	file = ""
	#constructor
	def __init__(self,file):
		self.file = str(file)
	#Get Methods
	def get_file(self):
		return self.file

	def set_file(self,file):
		self.file = str(file)

	def get_db(self):
		return self.db

	#Cursor Functions
	def build_db(self,file):
		db = getattr(g,'_database',None)
		if db is None:
			db = g._database = sqlite3.connect(file)
		return db

	def close_connection(self,exception):
	    db = getattr(g, '_database', None)
	    if db is not None:
	        db.close()

	def build_cursor(self):
		cursor = get_db().cursor()
		return cursor
	
	#QUERY FUNCTIONS

	def registration(self,firstname,surname,username,password,email,c):
		db = self.build_db(self.file)
		#works out time before query executes
		preQueryTime = SQLInjectionProtection.getCurrentTimeInSeconds()
		c.execute('SELECT COUNT(*) FROM User')
		count = c.fetchall()
		#works out user ID
		userCount = 0
		for i in count:
			userCount = i[0]
			userCount = userCount+1
		#sanitise inputs
		firstname = SQLInjectionProtection.querySanitise(firstname)
		surname = SQLInjectionProtection.querySanitise(surname)
		username = SQLInjectionProtection.querySanitise(username)
		password = SQLInjectionProtection.querySanitise(password)
		email = SQLInjectionProtection.querySanitise(email)
		#execute query
		query = "INSERT INTO User (FirstName,Surname,UserName,Password,Email,UID,isAdmin,isBanned) VALUES ('%s','%s','%s','%s','%s',%d,%d,%d);"%(firstname,surname,username,password,email,userCount,0,0)
		
		c.execute(query)
		db.commit()
		#ensures all queries take 0.025 seconds
		SQLInjectionProtection.delayQueryOutput(preQueryTime)


		#insert_db(query)

	def log_in(self,email,password,c,user):
		db = self.build_db(self.file)
		#sanitise inputs
		email = SQLInjectionProtection.querySanitise(email)
		password = SQLInjectionProtection.querySanitise(password)
		#works out time before query executes
		preQueryTime = SQLInjectionProtection.getCurrentTimeInSeconds()
		#gets hashed password from database
		passwordHashQuery = "SELECT Password from User WHERE Email = '%s'"%(email)
		c.execute(passwordHashQuery)
		passwordHashResultTuple = c.fetchone()
		passwordHash = '%s'%(passwordHashResultTuple)
		passwordHash = SQLInjectionProtection.decryptString(passwordHash)
		#checks if passwords entered by user matches hashed password in database
		if(check_password_hash(passwordHash, password)):
			#creates user 
			query = "SELECT * from User WHERE Email='%s';"%(email)
			c.execute(query)
			result = c.fetchall()
			#ensures all queries take 0.025 seconds
			SQLInjectionProtection.delayQueryOutput(preQueryTime)
			if not result:
				return False
			else:
				db.commit()
				for r in result:
					#decrypts sanitised data
					firstname = SQLInjectionProtection.decryptString(r[0])
					surname = SQLInjectionProtection.decryptString(r[1])
					username = SQLInjectionProtection.decryptString(r[2])
					password = SQLInjectionProtection.decryptString(r[3])
					email = SQLInjectionProtection.decryptString(r[4])
					#sets user object
					user.set_firstName(firstname)
					user.set_surName(surname)
					user.set_userName(username)
					user.set_password(password)
					user.set_email(email)
				return True

	#Generic Query Methods (Update, Select, Delete)

	def updateTable(self, cursor, table, updateVariableName, updateVariableValue, condition, conditionValue):
		#build database so changes can be commited
		db = self.build_db(self.file)
		#sanitise user entered values
		sanitisedUpdateVariableValue = SQLInjectionProtection.querySanitise(updateVariableValue)
		sanitisedConditionValue = SQLInjectionProtection.querySanitise(conditionValue)
		#works out time before query executes
		preQueryTime = SQLInjectionProtection.getCurrentTimeInSeconds()
		#construct the query
		query = f'''UPDATE {table} SET {updateVariableName} = "%s" WHERE {condition} = "%s"'''%(sanitisedUpdateVariableValue, sanitisedConditionValue)

		cursor.execute(query)
		#ensures all queries take 0.025 seconds
		SQLInjectionProtection.delayQueryOutput(preQueryTime)
		db.commit()	
	
	def selectFromTable(self, cursor, table, getVariableName, condition, conditionValue):
		#build database so changes can be commited
		db = self.build_db(self.file)
		#sanitise user entered values
		sanitisedConditionValue = SQLInjectionProtection.querySanitise(conditionValue)
		#works out time before query executes
		preQueryTime = SQLInjectionProtection.getCurrentTimeInSeconds()
		#construct the query
		query = f'''SELECT {getVariableName} FROM {table} WHERE {condition} = "%s"'''%(sanitisedConditionValue)
		cursor.execute(query)
		queryTuple = cursor.fetchone()
		#formats the tuple as a string
		result = '%s'%(queryTuple)
		decryptedResult = SQLInjectionProtection.decryptString(result)
		#ensures all queries take 0.025 seconds
		SQLInjectionProtection.delayQueryOutput(preQueryTime)
		return decryptedResult

	def deleteFromTable(self, cursor, table, getVariableName, condition, conditionValue):
		#build database so changes can be commited
		db = self.build_db(self.file)
		#sanitise user entered values
		sanitisedConditionValue = SQLInjectionProtection.querySanitise(conditionValue)
		#works out time before query executes
		preQueryTime = SQLInjectionProtection.getCurrentTimeInSeconds()
		#construct the query
		query = f'''DELETE {getVariableName} FROM {table} WHERE {condition} = "%s"'''%(sanitisedConditionValue)
		cursor.execute(query)
		#ensures all queries take 0.025 seconds
		SQLInjectionProtection.delayQueryOutput(preQueryTime)
		db.commit()

	#Specific Query Methods

	def ban_user(self, username, bannedStatus, c):
		#build database so changes can be commited
		db = self.build_db(self.file)
		#sanitise inputs
		username = SQLInjectionProtection.querySanitise(username)
		#works out time before query executes
		preQueryTime = SQLInjectionProtection.getCurrentTimeInSeconds()
		if username != 'ANiclaou':
			query = "UPDATE User SET isBanned =%d WHERE UserName = '%s';"%(bannedStatus,username)
			c.execute(query)
			#commits query update
			#ensures all queries take 0.025 seconds
			SQLInjectionProtection.delayQueryOutput(preQueryTime)
			db.commit()
		else:
			return None

	
	def makePost(self,text,username,c):
		preQueryTime = SQLInjectionProtection.getCurrentTimeInSeconds()
		postCount = self.getTotalNumberOfPosts()
		db2 = self.build_db(self.file)
		
		text = SQLInjectionProtection.querySanitise(text)
		username = SQLInjectionProtection.querySanitise(username)

		timestamp = time.asctime()
		timestamp = str(timestamp)
		#works out time before query executes
		
		query = "INSERT INTO Posting VALUES (%d,'%s','%s','%s');"%(postCount,text,timestamp, username)
		c.execute(query)
		db2.commit()
		
		searchQuery = "SELECT * FROM Posting WHERE PostID=%d"%(postCount)
		c.execute(searchQuery)
		db2.commit()
		result = c.fetchall()
		#ensures all queries take 0.025 seconds
		SQLInjectionProtection.delayQueryOutput(preQueryTime)
		if not result:
			return False
		else:
			return True	
		
	def getTotalNumberOfPosts(self):
		db = self.build_db(self.file)
		c = db.cursor()
		#works out time before query executes
		c.execute('SELECT COUNT(*) FROM Posting')
		count = c.fetchall()
		#ensures all queries take 0.025 seconds
		db.commit()
		postCount = 0
		for i in count:
			postCount = i[0]
			postCount = postCount+1
		return postCount

	def getPostList(self,c):
		#works out time before query executes
		preQueryTime = SQLInjectionProtection.getCurrentTimeInSeconds()
		query = "SELECT * FROM Posting;"
		c.execute(query)
		result = c.fetchall()
		postings = []
		for r in result:
			#sanitise inputs
			email = SQLInjectionProtection.decryptString(r[1])
			username = SQLInjectionProtection.decryptString(r[3])
			post1= Posts(r[0],email,r[2],username)
			#append to the front of the list
			postings = [post1] + postings
		#ensures all queries take 0.025 seconds
		SQLInjectionProtection.delayQueryOutput(preQueryTime)
		return postings
