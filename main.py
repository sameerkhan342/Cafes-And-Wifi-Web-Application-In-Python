from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, Email
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

@app.route("/")
def home():
    message = None
    if "user" in session:
        message = f"Welcome, {session['user']}!"
    return render_template("cafe_home.html", message=message)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    message = ""
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        with sqlite3.connect("cafes.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM register WHERE email=?", (email,))
            if c.fetchone():
                message = "Email already exists. Please login."
            else:
                c.execute("INSERT INTO register (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                conn.commit()
                return redirect(url_for("login"))
    return render_template("cafe_register.html", form=form, message=message)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    message = ""
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        with sqlite3.connect("cafes.db") as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM register WHERE email=? AND password=?", (email, password))
            user = c.fetchone()
            if user:
                session["user"] = user[0]
                return redirect(url_for("home"))
            else:
                message = "Incorrect credentials. Please register."
                
    return render_template("cafe_login.html", form=form, message=message)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route("/view")
def view():
    if "user" not in session:
        return redirect(url_for("login"))
    with sqlite3.connect("cafes.db") as conn:
        c = conn.cursor()
        c.execute("SELECT name, map_url, img_url, location, has_sockets, has_toilet, has_wifi, can_take_calls, seats, coffee_price FROM cafe")
        cafes = c.fetchall()
    return render_template("cafe_view.html", cafes=cafes)
    
if __name__ == "__main__":
    app.run(debug=True)
