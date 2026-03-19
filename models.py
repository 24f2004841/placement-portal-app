
from datetime import datetime
from enum import unique

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

db = SQLAlchemy()

class Drive_Status(Enum):
  Pending = "pending"
  Approved = "approved"
  Closed = "closed"

class Application_Status(Enum):
  Applied = "applied"
  Shortlisted = "shortlisted"
  Selected = "selected"
  Rejected = "rejected"

class Company_Status(Enum):
  Pending = "pending"
  Approved = "approved"
  Closed = "closed"

class User_Role(Enum):
  Company = "company"
  Student = "student"
  Admin = "admin"


class User(db.Model):
  __tablename__ = "users"
  id = db.Column(db.Integer , primary_key= True)
  username = db.Column(db.String(20), unique = True, nullable = False)
  email = db.Column(db.String(20), unique = True, nullable = False)
  password = db.Column(db.String(256), nullable = False)
  name = db.Column(db.String(20), nullable = False)
  role = db.Column(db.Enum(User_Role))
  status = db.Column(db.String(10), default='active')

  student_profile = db.relationship('Student', backref = 'user', useList = 'False', cascade = 'all, delete-orphan')
  company_profile = db.relationship('Company', backref = 'user', useList = 'False', cascade = 'all, delete-orphan')

class Student(db.Model):
  __tablename__ = "student"
  id = db.Column(db.Integer , primary_key = True)
  name = db.Column(db.String(20), nullable = False)
  age = db.Column(db.String(10) , nullable = False)
  department = db.Column(db.String(20), nullable=False)
  skills = db.Column(db.Text)
  
  organizations = db.relationship("Application", backref='student')
  drives = db.relationship("Drive", backref='student')

class Company(db.Model):
  __tablename__ = "company"
  id = db.Column(db.Integer , primary_key = True)
  name = db.Column(db.String(20), nullable = False)
  hr_contact = db.Column(db.String(10) , nullable = False)
  website = db.Column(db.String(20), nullable=False)

  status = db.Column(db.Enum(Company_Status), default=Company_Status.Pending)

  drives = db.relationship("Drive", backref= 'company')


class Drive(db.Model):
  __tablename__ = "drive"
  id = db.Column(db.Integer , primary_key = True)
  date = db.Column(db.DateTime, nullable = False , default = datetime.now)
  title = db.Column(db.String(20), nullable = False)
  description = db.Column(db.String(10) , nullable = False)
  eligibility = db.Column(db.String(20), nullable=False)
  deadline = db.Column(db.DateTime, nullable=False)
  status = db.Column(db.Enum(Drive_Status), default=Drive_Status.Pending)

  company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False, lazy=True)

  applications = db.relationship('Application', backref='drive')

class Application(db.Model):
  __tablename__ = "applications"
  id = db.Column(db.Integer , primary_key = True)
  drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable = False)
  student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable = False)
  description = db.Column(db.String(10) , nullable = False)
  date = db.Column(db.DateTime, nullable=False)

  status = db.Column(db.Enum(Application_Status), default=Application_Status.Applied)
  student = db.relationship('User', foregin_key=[student_id], backref='applications')
