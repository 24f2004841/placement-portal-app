from flask import Flask , render_template
from flask_login import LoginManager
from models import db, User
from seed import create_db

from routes.admin import admin_routes
from routes.student import student_routes
from routes.company import company

app = Flask(__name__)
login_manager = LoginManager()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db.init_app(app)
login_manager.init_app(app)

app.register_blueprint(admin_routes)
app.register_blueprint(student_routes)
app.register_blueprint(company)



@app.route('/')
def home():
  return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_admin():
  print("Adding Admin...")
  admin = User(name='admin', username='admin@mail.com', password_hash= 12345, role='admin', status='active')
  db.session.add(admin)
  db.session.commit()


if __name__ == "__main__":
  with app.app_context():
    db.create_all()
    create_db()
    if not User.query.filter_by(username='admin@mail.com').first():
      create_admin()
  app.run(debug = True)