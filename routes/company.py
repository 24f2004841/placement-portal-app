from flask import render_template, request, redirect, url_for, Blueprint, flash
from models import db, User, Company
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash , check_password_hash

company = Blueprint('company', __name__)

@company.route('/company_register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        name = request.form['Name'].strip()
        hr_contact = request.form['HRContact']
        username = request.form['Username'].strip().lower()
        password = request.form['Password']
        website = request.form['Website']

        # password_hash = generate_password_hash(password)

        user = User(name=name, password_hash=password, username=username, role='company', status='active')
        db.session.add(user)
        db.session.flush()

        user_id = User.query.filter_by(username=username).first().id
        company = Company(user_id=user_id, name=name, hr_contact=hr_contact, website=website )

        db.session.commit()
        flash(f'Account created for {name} with Username {username}!', 'success')
        login_user(user)

        return redirect(url_for('company.company_dashboard'))
    return render_template('register/company.html')
        
@company.route('/company_login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['Password']

        new_user = User.query.filter_by( username = username ).first()
        
        if new_user :

            if int(new_user.password_hash) == int(password) :
                login_user(new_user)
                return redirect(url_for('company.company_dashboard'))
            
            else :
                return render_template('error.html', message="wrong credentials")

        else:
            return render_template('error.html', message="Username not Found. First Register Yourself", retry_url=url_for('company.company_register'))

    return render_template('login/company.html')
        
@company.route('/company_dashboard', methods=['GET','POST'])
def company_dashboard():
    
    return render_template('company/dashboard.html')
