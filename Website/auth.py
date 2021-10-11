from Website import views
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=remember)                
                return redirect(url_for('views.index'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


    
@auth.route('/signup', methods=['GET','POST'])
def signup(): 
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
       
        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('This user already exists',category='error')
            
        elif len(email) < 10:
            flash('Email must be greater than 10 characters.', category='error')
           
        elif len(name) < 3:
            flash('Userame must be greater than 3 character.', category='error')
           
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # create a new user with the form data. Hash the password so the plaintext version isn't saved.
            new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'),description='',market_products='',users_follow_me='')
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)           
            flash('Account created!', category='success')
            return redirect(url_for('views.index'))
               
    return render_template('signup.html',user=current_user)


@auth.route('/')
@login_required
def logout():
    logout_user()
    return render_template("login.html",user=None)
