from flask import render_template, request, redirect, url_for, Blueprint, flash
from models import db, User, Student
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash , check_password_hash

student_routes = Blueprint('student', __name__)

@student_routes.route('/student_register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form['Name'].strip()
        age = int(request.form['Age'])
        username = request.form['Username'].strip().lower()
        password = request.form['Password']
        department = request.form['Department']
        skills = request.form['Skills']

        new_user = User(username=username, password_hash=password, role='student', status='active')
        db.session.add(new_user)
        db.session.flush()

        user_id = User.query.filter_by(username=username).first().id
        db.session.add(Student(user_id=user_id ,age=age, name=name, skills=skills, department=department))

        db.session.commit()
        flash(f'Account created for {name} with Username {username}!', 'success')
        login_user(new_user)

        return redirect(url_for('student_routes.student_dashboard'))

    return render_template('register/student.html')
        
@student_routes.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['Password']

        new_user = User.query.filter_by( username = username ).first()
        
        if  new_user:

            if new_user.password_hash == password:
                login_user(new_user)
                return redirect(url_for('student.student_dashboard'))
            
            else :
                return render_template('error.html', message="wrongs credentials")
                
        else:
            return render_template('error.html', message="Username not Found. First Register Yourself", retry_url=url_for('student.student_register'))


    return render_template('login/student.html')
        
@student_routes.route('/dashboard', methods=['GET','POST'])
def student_dashboard():

    return render_template('student/dashboard.html')
