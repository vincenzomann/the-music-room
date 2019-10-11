#set up mail server config
app.config['MAIL_SERVER'] = 'imap.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
#NOT SECURE - move to config file
app.config['MAIL_USERNAME'] = "2greeks1italian@gmail.com"
app.config['MAIL_PASSWORD'] = "asecurepasswordladz1"
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECRET_KEY'] = os.urandom(24)