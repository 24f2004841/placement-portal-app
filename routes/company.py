from flask import render_template, request, redirect, url_for, Blueprint, flash
from models import db, User, Company, Drive, Application, Student
from flask_login import login_user, logout_user , current_user, login_required
from werkzeug.security import generate_password_hash , check_password_hash
from datetime import datetime, timedelta, timezone


company = Blueprint('company', __name__)

@company.route('/company_register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        name = request.form['Name'].strip()
        hr_contact = request.form['HRContact']
        username = request.form['Username'].strip().lower()
        password = request.form['Password']
        website = request.form['Website']

        user = User(name=name, password_hash=password, username=username, role='company', status='pending')
        db.session.add(user)
        db.session.flush()

        user_id = User.query.filter_by(username=username).first().id
        db.session.add(Company(user_id=user_id, name=name, hr_contact=hr_contact, website=website ))

        db.session.commit()
        flash(f'Account created for {name} with Username {username}!', 'success')
        login_user(user)

        flash('You can Login when Approved by Admin','success')
        return redirect(url_for('home'))
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
            return render_template('error.html', 
            message="Username not Found. First Register Yourself", 
            retry_url=url_for('company.company_register'))

    else:
        return render_template('login/company.html')
        
@company.route('/company_dashboard', methods=['GET','POST'])
@login_required
def company_dashboard():
    if current_user.role == 'company' and current_user.status == 'active' :

        active_drive = Drive.query.filter(Drive.company_id == current_user.company.id , Drive.status == 'active').all()
        pending_drive = Drive.query.filter(Drive.company_id == current_user.company.id , Drive.status == 'pending').all()
        closed_drive = Drive.query.filter(Drive.company_id == current_user.company.id, Drive.status == 'closed').all()

        return render_template('company/dashboard.html',
            active_drive=active_drive,
            pending_drive=pending_drive,
            closed_drive=closed_drive
        )

    elif current_user.role == 'company' and current_user.status == 'pending':

        flash('You are not Approved yet by the Admin.', 'danger')
        return redirect(url_for('home'))

    else:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('home'))

    
@company.route('/company/drive/<int:drive_no>', methods=['GET','POST'])
@login_required
def company_drive(drive_no):
    if current_user.id == Drive.query.get(drive_no).company_id:

        applications = Application.query.filter( Application.drive_id == drive_no)
        drive = Drive.query.get(drive_no )
    
        return render_template('company/drive.html', drive_detail=drive, applications=applications)

    else:
        flash('You are authorized to access this Drive', 'danger')
        return redirect(url_for('home'))

@company.route('/company/drive/<int:drive_id>/application', methods=['GET','POST'])
@login_required
def company_view_application(drive_id):
    if current_user.id == Drive.query.get_or_404(drive_id).company_id:

        application_id = request.args.get('application_id')
        application = Application.query.filter_by(id=application_id, drive_id=drive_id).first()
        student_detail = Student.query.get(application.student_id)
        
        return render_template('company/view_application.html', student_detail=student_detail, application=application)

    else:
        flash('You are authorized to access this Application', 'danger')
        return redirect(url_for('home'))

@company.route('/company/update_application/<int:application_id>', methods=['POST'])
@login_required
def update_application_status(application_id):
    application = Application.query.get_or_404(application_id)
    status = request.form.get('Status')
    if status:
        application.status = status
        db.session.commit()
        flash(f'Application status updated to {status}.', 'success')
    return redirect(url_for('company.company_drive', drive_no=application.drive_id))



@company.route('/company/new_drive', methods=['GET','POST'])
@login_required
def new_drive():
    if request.method == 'POST':
        if current_user.role == 'company':
            if current_user.status == 'active':

                title = request.form['Title']
                description = request.form['Description']
                eligibility = request.form['Eligibility'].strip().lower()
                duration = int(request.form['Duration'])
                salary = int(request.form['Salary'])

                now = datetime.now(timezone.utc)
                new_drive = Drive(title=title, description=description,eligibility=eligibility,salary=salary,deadline= now + timedelta(days=duration), company_id=current_user.company.id)
                db.session.add(new_drive)
                db.session.commit()

                flash(f'Drive created', 'success')
                return redirect(url_for('company.company_dashboard'))

            else:
                flash('You are not Approved yet by the Admin.', 'danger')
                return redirect(url_for('home'))

        else:
            flash('You are not authorized to access this page.', 'danger')
            return redirect(url_for('home'))

    return render_template('company/new_drive.html')

@company.route('/company/drive/<int:drive_no>', methods=['GET','POST'])
def company_drive_close():
    if current_user.id == Drive.query.get_or_404(id).company_id:

        drive = Drive.query.get(drive_no)
        drive.status = 'closed'
        db.session.commit()
        flash(f'Your Drive is Closed Now','success')
        return render_template('company/dashboard.html')
    
    else:
        flash('You are authorized to access this Drive', 'danger')
        return redirect(url_for('home'))
        
