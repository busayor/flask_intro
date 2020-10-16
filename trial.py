from flask import Flask, redirect, url_for, render_template, request, session, flash
#  in order to make sessions last longer, import this lib
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#  in order to use session, you must set a secret key
app.secret_key = "l10nHear7"

#  in order to make sessions last longer, this below means it will last for 5 minutes
app.permanent_session_lifetime = timedelta(minutes=5)

#  configure the database using the code below
#  users represents the table you intend to query
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'

# disables notifications/warnings
app.config['SQLALCHEMY_TRACK_MMODIFICATIONS'] = False

# create a db as a model and give values
db = SQLAlchemy(app)
class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email

# default home page
@app.route("/")
def home():
    return render_template("index.html")


# page to render all the records of the users table
@app.route("/view")
def view():
    return render_template("view.html", values = users.query.all())

# login page
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # when creating your sessions, you must initialize the session.permanent = True
        session.permanent = True 
        user = request.form["nm"]
        session["user"] = user

        # insert user into db table if user does not exist, name of table here is users
        found_user = users.query.filter_by(name = user).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = users(user, " ")
            # use this to add the new user to the table
            db.session.add(usr)
            #  use this method to commit the new change(s) to the table
            db.session.commit()

        flash("Login successful!")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already logged in!")
            return redirect(url_for("user"))

        return render_template("login.html")


# user page - requires login, creates new session
@app.route("/user", methods=["GET", "POST"])
def user():
    email = None
    if "user" in session:
        user = session["user"]

        # here, we are about to receive the email from the use but first you must check the method type
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            # run query to fetch the users details and then update the email field
            found_user = users.query.filter_by(name = user).first()
            found_user.email = email
            db.session.commit()
            flash("Email successfully saved!")
        else:
            if "email" in session:
                email = session["email"]

        return render_template("user.html", email = email )
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


# logout page - destroys session and redirects to login
@app.route("/logout")
def logout():
    flash("You have been logged out!", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    # this next line creates a table if it does not already exists
    db.create_all()
    app.run(debug=True)