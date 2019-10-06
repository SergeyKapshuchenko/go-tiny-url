from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from models import User, Url
from app import app
from urllib.parse import urlparse
import short_url as surl


host = "https://go-tiny-url.herokuapp.com/"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def index_post():

    original_url = request.form.get('url')

    if not original_url:
        flash("Field is empty. Please put link here.")
        return render_template("index.html")

    if urlparse(original_url).scheme == '':
        url = 'http://' + original_url
    else:
        url = original_url

    if current_user.is_authenticated:
        email = current_user.email
    else:
        email = None

    url = Url.create(url=url, email=email)
    url.update()
    encoded_string = surl.encode_url(url.id)

    return render_template('index.html', short_url=host + encoded_string)


@app.route('/profile')
@login_required
def profile():
    data = Url.select().where(Url.email == current_user.email)
    links = [(host + surl.encode_url(data.id), data.url) for data in data]
    return render_template('profile.html', links=links)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():

    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.select().where(User.email == email).first()

    if not user or not user.check_password(password):
        flash('Please check your login and password')
        return redirect(url_for('login'))

    login_user(user, remember=remember)
    return redirect(url_for('profile'))


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_post():

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.select().where(User.email == email)

    if user:
        flash('Email address already exists')
        return render_template('signup.html', error=1)

    if not email or not name or not password:
        flash('Please fill in all fields')
        return render_template('signup.html', error=2)

    User.create(email=email, username=name, password=generate_password_hash(password))
    User.update()

    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/<short_url>')
def redirect_short_url(short_url):
    if short_url[-1] == "+":
        row = Url.select().where(Url.id == surl.decode_url(short_url[:-1])).first()
        if row:
            return render_template('stats.html', link=row)
        else:
            abort(404)

    row = Url.select().where(Url.id == surl.decode_url(short_url)).first()
    if row:
        Url.update(counter=Url.counter + 1).where(Url.id == row.id).execute()
        return redirect(row.url)
    else:
        abort(404)            # raises an error


@app.errorhandler(404)    # error handler convert it to response
def not_found(e):
    return render_template("404.html")


@app.route('/top')
def top():
    links = Url.select().order_by(Url.counter.desc())
    try:
        top = [(i, host + surl.encode_url(links[i].id), links[i].counter) for i in range(10)]
    except IndexError:
        top = [(i + 1, host + surl.encode_url(links[i].id), links[i].counter) for i in range(len(links))]
    return render_template('top.html', top=top)
