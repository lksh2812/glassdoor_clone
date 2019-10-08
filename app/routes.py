from app import app, celery
from flask import render_template, flash, redirect, url_for, request, g,\
    session
from app.forms import LoginForm, RegistrationEmployee, EditEmployeeProfileForm, \
    RegistrationEmployer, EditEmployerProfileForm, ReviewForm, SearchForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Employee, Employer, Review
from werkzeug.urls import url_parse
from app import db
from app import loginmanager
from flask import current_app
import csv
from flask import send_file
import os
import time

@app.route('/task_status')
def check_status(task):
    time.sleep(4)
    print(task.state)
    flash('Task done')
    # return redirect(url_for('employers', id=id))


@app.route('/get_file/<id>')
def get_file(id):
   task = celery.AsyncResult(id)
   url = task.result
   return {'url' : url}


@celery.task(name='download.review')
def download_review(id):
    file = os.getcwd()
    user = Employer.query.filter_by(id=id).first_or_404()
    reviews = user.reviews.order_by(Review.timestamp.desc())
    csv_data = []
    for review in reviews:
        csv_data.append([review.author, review.body])
    csv.register_dialect('myDialect', delimiter = '|', lineterminator = '\r\n\r\n')
    with open(os.path.join(file,'app/static/'+id+'reviews.csv'), 'w') as f:
        writer = csv.writer(f, dialect='myDialect')
        writer.writerows(csv_data)
    f.close()
    url = "/static/{}reviews.csv".format(user.id)
    return url


@app.route('/download/review/<id>')
def downloadreview(id):
    task = download_review.delay(id)
    return {'id': str(task)}


@app.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    employers = Employer.query.order_by(Employer.id.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=employers.next_num) \
        if employers.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if employers.has_prev else None
    return render_template('explore.html', title='Explore',
                           employers=employers.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/search')
def search():
    keyword = request.args['key']
    page = request.args.get('page', 1, type=int)
    employees, total = Employee.search(keyword, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('search', key=keyword, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('search', key=keyword, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', items=employees,
                           next_url=next_url, prev_url=prev_url)


@app.route('/employers/search')
def employerssearch():
    if not g.search_form.validate():
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    employers, total = Employer.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('employerssearch', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('employerssearch', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', items=employers,
                           next_url=next_url, prev_url=prev_url)


@app.before_request
def before_request():
    g.search_form = SearchForm()


@loginmanager.user_loader
def load_user(id):
    if session['isemployee']:
        return Employee.query.get(int(id))
    else:
        return Employer.query.get(int(id))


@app.route('/employers/profile', methods=['GET', 'POST'])
@login_required
def employersprofile():
    form = EditEmployerProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.domain = form.domain.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('employers', id=current_user.id))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('profile.html', title='Edit Profile',
                           form=form)


@app.route('/employers/<id>', methods=['GET', 'POST'])
@login_required
def employers(id):
    user = Employer.query.filter_by(id=id).first_or_404()
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(body=form.review.data, author=current_user, \
            subject=user, rating=int(form.rating.data))
        db.session.add(review)
        db.session.commit()
        flash('Your review is updated!')
        return redirect(url_for('employers', id=user.id))
    page = request.args.get('page', 1, type=int)
    rating = user.get_rating()
    reviews = user.reviews.order_by(Review.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('employers', id=user.id, page=reviews.next_num) \
        if reviews.has_next else None
    prev_url = url_for('employers', id=user.id, page=reviews.prev_num) \
        if reviews.has_prev else None
    return render_template('employer.html', user=user, form=form,\
        reviews=reviews.items, next_url=next_url, prev_url=prev_url, rating=rating)

@app.route('/register/employers', methods=['GET', 'POST'])
def registeremployers():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationEmployer()
    if form.validate_on_submit():
        user = Employer(username=form.username.data, email=form.email.data, domain=form.domain.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('loginemployers'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login/employers', methods=['GET', 'POST'])
def loginemployers():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Employer.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('loginemployers'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        session['isemployee'] = False
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, emp_login=False)


@app.route('/employees/profile', methods=['GET', 'POST'])
@login_required
def employeesprofile():
    form = EditEmployeeProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.work_for = form.work_for.data
        current_user.designation = form.designation.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('users', id=current_user.id))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('profile.html', title='Edit Profile',
                           form=form)


@app.route('/users/<id>', methods=['GET', 'POST'])
@login_required
def users(id):
    user = Employee.query.filter_by(id=id).first_or_404()
    return render_template('user.html', title='user', user=user)


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
    return render_template('register.html', title='Register', form=form)


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
        session['isemployee'] = True
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, emp_login=True)