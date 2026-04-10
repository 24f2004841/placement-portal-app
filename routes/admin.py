from flask import render_template, request, redirect, url_for, Blueprint, flash
from models import db, User, Student, Company, Drive, Application
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash , check_password_hash
from sqlalchemy import or_, String, cast

from routes import company


admin_routes = Blueprint('admin', __name__)

@admin_routes.route('/admin_login', methods=['GET','POST'])
def admin_login():
  if request.method == 'POST':
    username = request.form['Username']
    password = request.form['Password']

    admin = User.query.filter_by(username=username, role='admin').first()

    if password == admin.password_hash :
      login_user(admin)
      flash('Logged in successfully.')

      return redirect(url_for('admin.admin_dashboard'))

    return render_template('error.html',message='Wrong Credentials', retry_url = url_for('admin.admin_login'))

  return render_template('login/admin.html')

        
@admin_routes.route('/admin_dashboard', methods=['GET','POST'])
def admin_dashboard():
  if current_user.role == 'admin':

    search_query = request.args.get('q', '').strip()

    stats = {
        'cc': User.query.filter_by(role='company').count(),
        'sc': User.query.filter_by(role='student').count(),
        'cb': User.query.filter_by(role='company', status='blacklisted').count(),
        'sb': User.query.filter_by(role='student', status='blacklisted').count(),
        'cp': User.query.filter_by(role='company', status='pending').count(),
    }

    def fetch_company(query=None):
        base = Company.query.filter(Company.status == 'active')
        if query:
            base = base.filter(or_(
                Company.name.ilike(f'%{query}%'),
                cast(User.id, String).ilike(f'%{query}%')
            ))
        return base.all()

    def fetch_drives(query=None):
        if query:
            return Drive.query.filter(Drive.title.ilike(f'%{query}%')).all()
        return Drive.query.all()

    if search_query : 

      company_list = fetch_company(search_query)
      drive_list   = fetch_drives(search_query)
      stu_count = Student.query.count()
      com_count = Company.query.count()
      drive_count = Drive.query.count()
      app_count = Application.query.count()

    else : 
      company_list = Company.query.filter_by(status='active')
      stu_count = Student.query.count()
      com_count = Company.query.count()
      drive_count = Drive.query.count()
      app_count = Application.query.count()
  
  return render_template(
      'admin/dashboard.html',
      **stats,
      companies=company_list,
      search_query=search_query,
      stu_count=stu_count,
      com_count  = com_count,
      drive_count = drive_count,
      app_count = app_count
  )

@admin_routes.route('/all_students', methods=['GET','POST'])
def all_students():
  if current_user.role == 'admin':

    search_query = request.args.get('q', '').strip()

    stats = {
        'cc': User.query.filter_by(role='company').count(),
        'sc': User.query.filter_by(role='student').count(),
        'cb': User.query.filter_by(role='company', status='blacklisted').count(),
        'sb': User.query.filter_by(role='student', status='blacklisted').count(),
        'cp': User.query.filter_by(role='company', status='pending').count(),
    }

    def fetch_student(query=None):
        base = Student.query.filter(Student.user.has(status='active'))
        if query:
            base = base.filter(or_(
                Student.name.ilike(f'%{query}%'),
                cast(Student.user_id, String).ilike(f'%{query}%')
            ))
        return base.all()

    if search_query:
      students = fetch_student(search_query)

    else:
      students = Student.query.all()

    return render_template('admin/total_students.html', students=students)

  else:
    flash('You are authorized to access this page', 'danger')
    return redirect(url_for('app'))

@admin_routes.route('/job_applications', methods=['GET', 'POST'])
def job_applications():
  if current_user.role == 'admin':

    applications = Application.query.all()

    return render_template('admin/job_application.html', applications=applications)

  else:
    flash('You are authorized to access this page', 'danger')
    return redirect(url_for('app'))

@admin_routes.route('/approve_job_application/<int:app_id>', methods=['GET', 'POST'])
def approve_job_application(app_id):
  if current_user.role == 'admin':

      app = Application.query.get(app_id)
      app.status = 'accepted'
      db.session.commit()


      return redirect(url_for('admin.admin_drive'))

  else:
    flash('You are authorized to access this page', 'danger')
    return redirect(url_for('app'))

@admin_routes.route('/reject_job_application/<int:app_id>', methods=['GET','POST'])
def reject_job_application(app_id):
  if current_user.role == 'admin':

    app = Application.query.get(app_id)
    app.status = 'rejected'
    db.session.commit()

    return redirect(url_for('admin.admin_drive'))

  else:
    flash('You are authorized to access this page', 'danger')
    return redirect(url_for('app'))

@admin_routes.route('/pending_companies', methods=['GET', 'POST'])
def pending_companies():
  if current_user.role == 'admin':

    companies = Company.query.filter_by(status='pending').all()

  else:
    flash('You are not authorized to access this page.', 'danger')
    return redirect(url_for('app'))

  return render_template('admin/pending_companies.html', companies = companies)

@admin_routes.route('/approve_company/<int:user_id>', methods=['POST'])
def approve_company(user_id):
  if current_user.role == 'admin':
    user = User.query.get(user_id)
    user.status = 'active'
    user.company.status = 'active'
    db.session.commit()

    return redirect(url_for("admin.pending_companies"))
  
  else :
      flash('You are not authorized to access this page.', 'danger')
      return redirect(url_for('app'))


@admin_routes.route('/reject_company/<int:user_id>', methods=['POST'])
def reject_company(user_id):
  if current_user.role == 'admin':
    user = Company.query.get(user_id)
    user.status = 'blacklist'
    db.session.commit()

    return redirect(url_for("admin.pending_companies"))
  
  else :
    flash('You are not authorized to access this page.', 'danger')
    return redirect(url_for('app'))


@admin_routes.route('/all_drives', methods=['GET', 'POST'])
def admin_drive():
  if current_user.role == 'admin':
    pending_drives = Drive.query.filter_by(status='pending')
    ongoing_drives = Drive.query.filter_by(status='active')
    closed_drives = Drive.query.filter_by(status = 'closed')
    
    return render_template('admin/admin_drives.html', 
    pending_drives = pending_drives, 
    ongoing_drives = ongoing_drives,
    closed_drives = closed_drives)

  else:
      flash('You are not authorized to access this page.', 'danger')
      return redirect(url_for('home'))

@admin_routes.route('/approve_drive/<int:drive_id>', methods=['GET', 'POST'])
@login_required
def approve_drive(drive_id):
  if current_user.role == 'admin':
    print(drive_id)
    drive = Drive.query.get(drive_id)
    print(drive)
    drive.status = 'active'
    db.session.commit()

    return redirect(url_for('admin.admin_drive'))
  
  else:
      flash('You are not authorized to access this page.', 'danger')
      return redirect(url_for('home'))

@admin_routes.route('/reject_drive/<int:drive_id>', methods=['GET', 'POST'])
def reject_drive(drive_id):
  if current_user.role == 'admin':
    drive = Drive.query.get(drive_id)
    drive.status = 'closed'
    db.session.commit()

    return redirect(url_for('admin.admin_drive'))
  
  else:
      flash('You are not authorized to access this page.', 'danger')
      return redirect(url_for('home'))

@admin_routes.route('/delete_drive/<int:drive_id>', methods=['GET', 'POST'])
def delete_drive(drive_id):
  if current_user.role == 'admin':
    drive = Drive.query.filter_by(id = drive_id)
    drive.status = 'closed'
    db.session.commit()
    
    return redirect(url_for('admin.admin_drive'))

  else:
      flash('You are not authorized to access this page.', 'danger')
      return redirect(url_for('home'))

@admin_routes.route('/blacklist/<int:user_id>', methods=['POST'])
def admin_blacklist(user_id):
    if current_user.role == 'admin':
        users = User.query.get(int(user_id))
        if users.role == 'company':
          company = Company.query.filter_by(user_id=user_id).first()
          users.status = 'blacklist'
          company.status = 'blacklist'
          flash(f'{company.name} has been blacklisted! And all the drives has deleted', 'dark')

          drives = Drive.query.filter_by(company_id=company.id).all()
          for drive in drives:
              Application.query.filter_by(drive_id=drive.id).delete()
              db.session.delete(drive)

        elif users.role == 'student':
          stu = Student.query.filter_by(user_id=user_id).first()
          users.status = 'blacklist'
          flash(f'Student {stu.name} has been blacklisted!', 'dark')

        db.session.commit()
        return redirect(url_for('admin.admin_dashboard'))
        
    else:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('home'))


@admin_routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

