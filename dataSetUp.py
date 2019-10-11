from flask import Flask
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

connection = sqlite3.connect('database1.db')
cursor = connection.cursor()

password = generate_password_hash('asecurepasswordladz1')

cursor.execute('CREATE TABLE User (FirstName varchar(255) NOT NULL,Surname varchar(255) NOT NULL,UserName varchar(255) UNIQUE NOT NULL,Password varchar(255) NOT NULL,Email varchar(255) UNIQUE NOT NULL,UID bigint(255),isAdmin BIT NOT NULL,isBanned BIT NOT NULL)')
cursor.execute('INSERT INTO User VALUES (?,?,?,?,?,?,?,?)',('Andrew','Nicolaou','ANiclaou',password,'2greeks1italian{0x40}gmail{0x2e}com','1',1,0))
connection.commit()
cursor.execute('CREATE TABLE Posting(PostID bigint UNIQUE NOT NULL, Content varchar(1700) NOT NULL,DateStamp varchar(255) NOT NULL, Username varchar(255) NOT NULL)')
connection.commit()