from app import app
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationEmployee, EditEmployeeProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Employee, Employer
from werkzeug.urls import url_parse
from app import db


@app.route('/edit_employee_profile', methods=['GET', 'POST'])
@login_required
def edit_employee_profile():
    form = EditEmployeeProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.work_for = form.work_for.data
        current_user.designation = form.designation.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_employee_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_employee_profile.html', title='Edit Profile',
                           form=form)

@app.route('/user/<id>')
@login_required
def user(id):
    user = Employee.query.filter_by(id=id).first_or_404()
    return render_template('user.html', user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationEmployee()
    if form.validate_on_submit():
        user = Employee(username=form.username.data, email=form.email.data, work_for=form.work_for.data, designation=form.designation.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register_employee.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Employee.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)