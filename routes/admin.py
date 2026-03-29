from flask import render_template, request, redirect, url_for, Blueprint, flash
from models import db, User
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash , check_password_hash


admin_routes = Blueprint('admin', __name__)

@admin_routes.route('/admin_login', methods=['GET','POST'])
def admin_login():
  if request.method == 'POST':
    username = request.form['Username']
    password = request.form['Password']

    # password_hash = generate_password_hash(password)

    admin = User.query.filter_by(username=username, role='admin').first()

    # if admin and admin.check_password_hash(password):
    print(type(admin.password_hash), type(password))

    if password == admin.password_hash :
      login_user(admin)
      flash('Logged in successfully.')

      redirect(url_for('admin.admin_dashboard'))

    return render_template('error.html',message='Wrong Credentials', retry_url = url_for('admin.admin_login'))

  return render_template('login/admin.html')

        
@admin_routes.route('/admin_dashboard', methods=['GET','POST'])
def admin_dashboard():
    
    return render_template('admin/dashboard.html')
