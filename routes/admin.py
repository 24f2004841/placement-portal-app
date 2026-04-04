from flask import render_template, request, redirect, url_for, Blueprint, flash
from models import db, User, Student, Company, Drive
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

    VISIBLE_STATUSES = ['active', 'warning']

    def fetch_users(role, query=None):
        base = User.query.filter(User.role == role, User.status.in_(VISIBLE_STATUSES))
        if query:
            base = base.filter(or_(
                User.name.ilike(f'%{query}%'),
                cast(User.id, String).ilike(f'%{query}%')
            ))
        return base.all()

    def fetch_drives(query=None):
        if query:
            return Drive.query.filter(Drive.title.ilike(f'%{query}%')).all()
        return Drive.query.all()

    if search_query : 

      company_list = fetch_users('company', search_query)
      drive_list   = fetch_drives(search_query)

    else : 
      company_list = Company.query.filter_by(status='active')
  
  return render_template(
      'admin/dashboard.html',
      **stats,
      companies=company_list,
      search_query=search_query
  )


@admin_routes.route('/job_applications', methods=['GET', 'POST'])
def job_applications():


  return render_template('admin/job_applications.html')


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
    user.status = 'approved'
    db.session.commit()

    return redirect(url_for("admin.pending_companies"))
  
  else :
      flash('You are not authorized to access this page.', 'danger')
      return redirect(url_for('app'))


@admin_routes.route('/reject_company/<int:user_id>', methods=['POST'])
def reject_company(user_id):
  if current_user.role == 'admin':
    user = User.query.get(user_id)
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
    
  else:
      flash('You are not authorized to access this page.', 'danger')
      return redirect(url_for('app'))

  return render_template('admin/admin_drives.html', pending_drives = pending_drives, ongoing_drives = ongoing_drives)

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

@admin_routes.route('/reject_drive/<int:drive_id>', methods=['GET', 'POST'])
@login_required
def reject_drive(drive_id):
  if current_user.role == 'admin':
    drive = Drive.query.filter_by(id = drive_id)
    drive.status = 'rejected'
    db.session.commit()

    return redirect(url_for('/admin.admin_drive'))

@admin_routes.route('/delete_drive/<int:drive_id>', methods=['GET', 'POST'])
@login_required
def delete_drive(drive_id):
  if current_user.role == 'admin':
    drive = Drive.query.filter_by(id = drive_id)
    db.session.delete(drive)

    return redirect(url_for('/admin.admin_drive'))


@admin_routes.route('/blacklist/<int:com_id>', methods=['POST'])
@login_required
def admin_blacklist(com_id):
    if current_user.role == 'admin':
        # user = User.query.get(user_id)
        company = Company.query.get(com_id)
        company.status = 'blacklisted'
        # user.status = 'blacklisted'

        db.session.commit()
        drives = Drive.query.filter_by(company_id=user.id).all()
        for drive in drives :
            db.session.delete(drive)

        if user.role == 'student':
            flash(f'Student {user.name} has been blacklisted!', 'dark')
            
        elif user.role == 'company':
            flash(f'Company {user.name} has been blacklisted!', 'dark')
            
        db.session.commit()
        return redirect(url_for('admin.admin_dashboard'))
        
    else:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('app'))


