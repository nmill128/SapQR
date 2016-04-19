
from wtforms import Form, TextField, PasswordField, validators, RadioField, Field, IntegerField
from werkzeug.security import check_password_hash, generate_password_hash
from flask.ext.pymongo import PyMongo
import app




class User():

    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

	def hash_password(password):
		return generate_password_hash(password)
		
class LoginForm(Form):
	username = TextField('Username', [validators.Required()])
	password = PasswordField('Password', [validators.Required()])
	
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.user = None	
		
	def validate(self):
		rv = Form.validate(self)
		if not rv:
			return False
		userEntry = app.mongo.db.users.find_one({'username': self.username.data})
        #user = User.query.filter_by(
        #    username=self.username.data).first()
		if userEntry is None:
			self.username.errors.append('Unknown username')
			return False
		user = User(userEntry["username"])

		if not user.validate_login(userEntry["password"], self.password.data):
			self.password.errors.append('Invalid password')
			return False

		self.user = user
		return True
		
class CreateLoginForm(Form):
	username = TextField('Username', [validators.Required()])
	password1 = PasswordField('Password1', [validators.Required()])
	password2 = PasswordField('Password2', [validators.Required()])
	gender = Field('Gender', [validators.Required()])
	age = IntegerField('Age', [validators.Required()])
	session_id = Field('Session Id', [validators.Required()])
	
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.user = None	
		
	def validate(self):
		rv = Form.validate(self)
		if not rv:
			return False
		if not self.password1.data == self.password2.data:
			return False
		userEntry = app.mongo.db.users.find_one({'username': self.username.data})
		if userEntry:
			return False
		doc =  {'username': self.username.data,
				'gender':self.gender.data,
				'age':self.age.data,
				'password': generate_password_hash(self.password1.data),
				'facilitator': False,
				'session_id': self.session_id.data}
		try:
			app.mongo.db.users.insert(doc)
		except pymongo.errors.DuplicateKeyError as e:
			return False
		user = User(self.username.data)
		self.user = user
		return True