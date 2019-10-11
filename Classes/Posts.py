class Posts:
	postID = 0
	content = ""
	timestamp = ""
	username = ""

	#constructor
	def __init__(self,postID,content,timestamp, username):
		self.postID = postID
		self.content = str(content)
		self.timestamp = str(timestamp)
		self.username = str(username)

	#get methods
	def get_postID(self):
		return self.postID

	def get_content(self):
		return self.content

	def get_timestamp(self):
		return self.timestamp

	def get_username(self):
		return self.username

	#set methods
	def set_postID(self,postID):
		self.postID = postID

	def set_content(self,content):
		self.content = str(content)

	def set_timestamp(self,timestamp):
		self.timestamp = str(timestamp)

	def set_username(self,username):
		self.username = str(username)