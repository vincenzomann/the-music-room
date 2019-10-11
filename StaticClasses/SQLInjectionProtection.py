from flask import Flask, g , request
import sqlite3
import datetime
import time
import re
from Classes.User import User
from Classes.Posts import Posts

class SQLInjectionProtection:

	#Dleays query to help avoid account enum and SQL injection
	def delayQueryOutput(preQueryTime):
		CurrentTime = datetime.datetime.now()
		CurrentTimeInSeconds = CurrentTime.second
		difference = CurrentTimeInSeconds-preQueryTime
		desiredQueryReturnTimeInSeconds = 0.025
		timeDelay = desiredQueryReturnTimeInSeconds-difference
		if timeDelay >= 0:
			time.sleep(timeDelay)

	def getCurrentTimeInSeconds():
		CurrentTime = datetime.datetime.now()
		CurrentTimeInSeconds = CurrentTime.second
		return CurrentTimeInSeconds

	#sanitises input using regex
	def querySanitise(userInputString):
		sanitiseInput = re.findall("[a-zA-Z0-9*{*}]", userInputString)
		for char in userInputString:
			hexChar = hex(ord(char))
			if char not in sanitiseInput:
				salt = "{"
				pepper = "}"
				crypt = salt+hexChar+pepper
				userInputString = userInputString.replace(char,crypt)
		return userInputString

	def decryptString(dbInputString):
		hexList = re.findall("{0x.*?}",dbInputString)
		for w in hexList:
			#removes placeholder "{"
			w1 = w.replace("{","")
			#removes placeholder "}"
			w2 = w1.replace("}","")
			#the hex value is currently a string, to ascii value
			wordHexInt = int(w2,16)
			#converts the ascii value to a char
			wordHexString = chr(wordHexInt)
			#replaces new char with old
			dbInputString = re.sub(w,wordHexString,dbInputString)
		return dbInputString 