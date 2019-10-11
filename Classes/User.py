class User:
	firstName= ""
	secondName= ""
	userName= ""
	email= ""
	password= ""
	isAdmin= 0
	#constructor
	def __init__(self,fName,sName,uName,pword,e,isAdmin):
		self.firstName = str(fName)
		self.secondName = str(sName)
		self.userName = str(uName)
		self.password = str(pword)
		self.email = str(e)
		self.isAdmin = isAdmin

	#get methods
	def get_firstName(self):
		return self.firstName

	def get_surName(self):
		return self.secondName

	def get_userName(self):
		return self.userName

	def get_email(self):
		return self.email

	def get_password(self):
		return self.password

	#set methods
	def set_firstName(self,firstName):
		self.firstName = str(firstName)

	def set_surName(self,secondName):
		self.secondName = str(secondName)

	def set_userName(self,userName):
		self.userName = str(userName)

	def set_email(self,email):
		self.email = str(email)

	def set_password(self,password):
		self.password = str(password)

	def set_isAdmin(self,isAdmin):
		self.isAdmin = isAdmin
