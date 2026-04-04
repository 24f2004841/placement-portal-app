from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from datetime import datetime , timezone 

# @login_manager.user_loader
# def load_user(user_id):
#     try:
#         return User.query.get(user_id)
#     except:
#         return None

db = SQLAlchemy()

class User(db.Model, UserMixin):
  __tablename__ = "user"
  id = db.Column(db.Integer , primary_key= True)
  username = db.Column(db.String(20), unique = True, nullable = False)
  name = db.Column(db.String(20), nullable=False)
  password_hash = db.Column(db.String(256), nullable = False)
  role = db.Column(db.String(10), nullable = False)
  status = db.Column(db.String(10), default='active')

  student_profile = db.relationship('Student', backref = 'user', uselist = False, cascade = 'all, delete-orphan')
  company_profile = db.relationship('Company', backref = 'user', uselist = False, cascade = 'all, delete-orphan')

class Student(db.Model):
  __tablename__ = "student"
  id = db.Column(db.Integer , primary_key = True)
  name = db.Column(db.String(20), nullable = False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)
  age = db.Column(db.String(10) , nullable = False)
  department = db.Column(db.String(20), nullable=False)
  skills = db.Column(db.Text)
  

class Company(db.Model):
  __tablename__ = "company"
  id = db.Column(db.Integer , primary_key = True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)
  name = db.Column(db.String(20), nullable = False)
  hr_contact = db.Column(db.String(10) , nullable = False)
  website = db.Column(db.String(20), nullable=False)
  status = db.Column(db.String(10), default='active')



class Drive(db.Model):
  __tablename__ = "drive"
  id = db.Column(db.Integer , primary_key = True)
  date = db.Column(db.DateTime, nullable = False , default = datetime.now(timezone.utc))
  title = db.Column(db.String(20), nullable = False)
  description = db.Column(db.String(10) , nullable = False)
  salary = db.Column(db.Integer, nullable=False)
  eligibility = db.Column(db.String(20), nullable=False)
  deadline = db.Column(db.DateTime, nullable=False)
  status = db.Column(db.String(20), nullable=False, default='pending')

  company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'))

  company_drive = db.relationship('Company', backref='drive')

  # job = db.relationship('Job', backref='drive', uselist=False, lazy=True, cascade="all, delete-orphan")

class Application(db.Model):
  __tablename__ = "applications"
  id = db.Column(db.Integer , primary_key = True)
  drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable = False)
  # job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'))
  student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
  description = db.Column(db.String(10) , nullable = False)
  date = db.Column(db.DateTime, nullable=False)
  status = db.Column(db.String(20), nullable=False, default='pending')

  student = db.relationship('Student', backref='applications')

  __table_args__ = (db.UniqueConstraint('drive_id', 'student_id', name='_job_student_uc'),)

# class Job(db.Model):
#     __tablename__ = 'jobs'
#     id = db.Column(db.Integer, primary_key=True)
#     drive_id = db.Column(db.Integer, db.ForeignKey('drive.id', ondelete='CASCADE'), nullable=False) 
#     company_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
#     title = db.Column(db.String(200), nullable=False)
#     description = db.Column(db.Text, nullable=False)
#     salary = db.Column(db.String(100))
#     interview_mode = db.Column(db.String(100), default='in-person')
#     category = db.Column(db.String(100))
#     is_active = db.Column(db.Boolean, default=True)
#     created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

#     applications = db.relationship('Application', backref='job', lazy=True, cascade="all, delete-orphan")
   
