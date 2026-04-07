from flask import render_template, request, redirect, url_for, Blueprint, flash
from models import db, User, Student, Company, Drive, Application
from flask_login import login_user, logout_user, login_required,current_user
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

        new_user = User(name=name, username=username, password_hash=password, role='student', status='active')
        db.session.add(new_user)
        db.session.flush()

        user_id = User.query.filter_by(username=username).first().id
        db.session.add(Student(user_id=user_id ,age=age, name=name, skills=skills, department=department))

        db.session.commit()
        flash(f'Account created for {name} with Username {username}!', 'success')
        login_user(new_user)

        return redirect(url_for('student.student_dashboard'))

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
    companies = Company.query.filter_by(status='active')

    applied_drives = Application.query.filter_by(student_id = current_user.id)

    return render_template('student/dashboard.html', companies=companies,app_drives=applied_drives)

@student_routes.route('/student/edit_profile', methods=['GET','POST'])
def edit_profile():
    if request.method == 'POST':
        if current_user.role == 'student' :
            department = request.form['Department']
            skills = request.form['Skills']
            age = request.form['Age']

            student = Student.query.get(stu_id)
            student.department = department
            student.skills = skills
            student.age = age
            db.session.commit()

            flash('Details Updated','success')
            return render_template('student/profile_edit.html')

        else :
            flash('You are authorized to access the Page','danger')
            return redirect(url_for('home'))

    else :
        flash('This is not POST request','danger')
        return redirect(url_for('home'))


@student_routes.route('/student/<int:com_id>/drives', methods=['GET','POST'])
def view_drives(com_id):
    drives = Drive.query.filter_by(company_id = com_id)
    company = Company.query.get(com_id)

    return render_template('student/drives.html', drives=drives, company=company)

@student_routes.route('/student/drive/<int:drive_id>', methods=['GET','POST'])
def view_drive(drive_id):
    drive_detail = Drive.query.get(drive_id)
    
    return render_template('student/drive_details.html', drive_detail=drive_detail)


@student_routes.route('/student/history',methods=['GET'])
def student_history():
    stu_id = request.args.get('stu_id')
    if current_user.id == int(stu_id):
        stu_app = Application.query.filter_by(student_id=stu_id)

        return render_template('student/history.html', applications=stu_app)

    else:
        flash('You are authorized to access this Application', 'danger')
        return redirect(url_for('home'))

@student_routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))