from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import werkzeug
from openai_class import my_openai
import time
from flask_login import LoginManager
import requests
import os
from linkedinapi import linkapi
from dotenv import load_dotenv

load_dotenv()

login_manager = LoginManager()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE IN DB


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register',methods=['GET', 'POST'])
def register():
    email = request.form.get('email')
    result = db.session.execute(db.select(User).where(User.email == email))
    # Note, email in db is unique so will only have one result.
    user = result.scalar()
    if user:
        # User already exists
        flash("You've already signed up with that email, log in instead!")
        return redirect(url_for('login'))
    if request.method=='POST':
        password = request.form['password']
        password = werkzeug.security.generate_password_hash(password, method='pbkdf2:sha256', salt_length = 8)
        user = User(
            email = request.form['email'],
            password = password,
            name = request.form['name']
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return render_template("secrets.html", name=request.form.get('name'))
    return render_template("register.html")

namee = ''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        

        if not user:
            flash('please register.')
            return render_template("login.html")
        elif check_password_hash(user.password, password):
            login_user(user)
            global namee
            namee = user.name
            return render_template("secrets.html", name=user.name)
        else:
            flash('could not log in please check your email/password or register.')
            return render_template("login.html")

    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    
    return render_template("secrets.html", logged_in=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/submitted', methods=['POST'])
@login_required
def submitted():
    prompt = request.form['prompt']
    img_url = request.form['image']
    ai_generator = my_openai(prompt)
    generated_text = ai_generator.generate_text()
    insta_token = os.getenv('insta_access_token')
    insta_id = os.getenv('insta_id')

    url_post_id = f'https://graph.facebook.com/v20.0/{insta_id}/media'

    data = {
        'image_url': img_url,
        'caption': generated_text,
        'access_token': insta_token
    }

    response = requests.post(url_post_id, json=data)

    post_id = response.json()['id']

    post_url = 'https://graph.facebook.com/v20.0/17841469165933820/media_publish'

    post_data = {
        'creation_id': post_id,
        'access_token': insta_token 
    }

    requests.post(post_url, json=post_data)

    link_post = linkapi(generated_text)
    status = link_post.postfeed()


    print(response.status_code)
    if response.status_code == 200 and status==201:
        global namee
        return render_template("successful.html", logged_in=True, name=namee)
    else:
        return render_template("failed.html", logged_in=True, name=namee)

@app.route('/download')
@login_required
def download():
    return send_from_directory('static', path="files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
