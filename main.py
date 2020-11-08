"""
Latest Edit: October 13, 2020

SGI

pip3 install -r requirements.txt

requirements.txt
 - pip freeze > requirements.txt

"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

#Import libraries
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, FloatField, DateTimeField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


#--------------------------------------------------------------------------------------------------------------------------------------------
app = Flask(__name__) # Start of Flask App
bootstrap = Bootstrap(app) # For WTForms
app.config['SECRET_KEY'] = 'temporarykey123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Ignore Warning message
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3' # db Will show up in this directory
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:looper04@localhost/sgi_iot'
db = SQLAlchemy(app) # Initialize SQLAlchemy app

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Class that represents user database ==========================================================================================================
class Sgi(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

class Truck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    truck_id = db.Column(db.String(50))
    truck_gps = db.Column(db.Float)
    truck_temp = db.Column(db.Float)
    truck_hum = db.Column(db.Float)
    truck_dt = db.Column(db.DateTime)

class Whouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    whouse_id = db.Column(db.String(50))
    whouse_temp = db.Column(db.Float)
    whouse_hum = db.Column(db.Float)
    whouse_dt = db.Column(db.DateTime)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Float)
    type = db.Column(db.String(50))
    produce = db.Column(db.String(50))
    buy_price = db.Column(db.Float)
    kilo = db.Column(db.Float)
    buy_dt = db.Column(db.DateTime)

class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    customer_id = db.Column(db.String(50))
    type = db.Column(db.String(50))
    produce = db.Column(db.String(50))
    price = db.Column(db.Float)
    kilo = db.Column(db.Float)
    name = db.Column(db.String(50))
    address = db.Column(db.String(50))
    contact = db.Column(db.Float)
    sale_dt = db.Column(db.Float)
    delivery_dt = db.Column(db.Float)

"""
Initialize in Terminal with Python to make the User db above

>>> from main import db
>>> db.create_all()

"""

@login_manager.user_loader
def load_user(user_id):
    return Sgi.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Enter Username', validators=[InputRequired(), Length(min=4, max=80)])
    password = PasswordField('Enter Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=30)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80),
                                                    EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

class InventoryForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    farm_id = StringField('Farm_id', validators=[InputRequired(), Length(min=2, max=30)])
    type = StringField('Type of Produce', validators=[InputRequired(), Length(min=2, max=30)])
    produce = StringField('Produce', validators=[InputRequired(), Length(min=2, max=30)])
    buy_price = FloatField('Buy Price', validators=[InputRequired(), Length(min=2, max=30)])

class SalesForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    name = StringField('Name', validators=[InputRequired(), Length(min=4, max=30)])
    type = StringField('Type', validators=[InputRequired(), Length(min=4, max=30)])
    produce = StringField('Produce', validators=[InputRequired(), Length(min=4, max=30)])
    price = FloatField('Sell Price', validators=[InputRequired()])
    kilo = FloatField('Kilograms', validators=[InputRequired()])
    address = StringField('Delivery Address', validators=[InputRequired(), Length(min=4, max=30)])
    contact = FloatField('Contact Number', validators=[InputRequired()])
    delivery_dt = FloatField('Delivery Date ', validators=[InputRequired()])

# Connecting to www.website.com/home
@app.route("/home")
@app.route('/')
def index():
    #user = db.session.query(Sgi.username)
    return render_template('home.html')

@app.route('/basket', methods=['GET', 'POST'])
def basket():

    form = SalesForm()
    if form.validate_on_submit():
        record = Sales(email=form.email.data,
                       name=form.name.data,
                       type=form.type.data,
                       produce=form.produce.data,
                       price=form.price.data,
                       kilo=form.kilo.data,
                       address=form.address.data,
                       contact=form.contact.data,
                       delivery_dt=form.delivery_dt.data,
                       )

        db.session.add(record)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('basket.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Sgi.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = Sgi(username=form.username.data,
                        email=form.email.data,
                        password=hashed_password,
                        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)



@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        try:
            crop = request.form['crops']
            region = request.form['region']
        except:
            redirect(url_for('dashboard'))

    return render_template('dashboard.html', name=current_user.username)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ================================================================================================================================================================================================

#---------------------------------------------------------------------------------------------------------------------------------------------
# End of Flask App
if __name__ == "__main__":
#    app.run(host='0.0.0.0')
   app.run(debug=True)
