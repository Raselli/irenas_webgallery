from . import db
from .database import Users, Artists
from flask import Blueprint, render_template, request, flash
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import redirect 
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint("auth", __name__)


# Login
@auth.route("/login", methods=["GET", "POST"])
def login(): 
    # method = POST: submit login
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check for empty
        if (username == "") or (password == ""):
            flash("Enter Username and Password.")
            return redirect(request.url)
        
        # Proceed: Submit
        else:
            user = Users.query.filter_by(username=username).first()
            if user:
                # Login
                if check_password_hash(user.password, password):
                    flash("Logged in.")
                    login_user(user, remember=True)
                    return render_template("manage_entries/overview.html")

                # Invalid Password
                else: 
                    flash("Invalid Username or Password.")
                    return redirect(request.url)

            # Invlaid Username
            else: 
                flash("Invalid Username or Password.")
                return redirect(request.url)        
    
    # method = GET: promt login
    else:
        if current_user.is_authenticated:
            return redirect("/overview")
        else:
            return render_template("authentication/login.html")


# Logout:
@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect("/login")


# Create Login
@auth.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    
    # method = POST: submit sign_up
    if request.method == "POST":
        username = request.form.get("username").strip()
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        display_name = request.form.get("display_name").strip()
        user = Users.query.filter_by(username=username).first()
        artist = Artists.query.filter_by(display_name=display_name).first()
        
        # Check: Username availability
        if user:
            flash("Username taken.")
            return redirect("/sign_up")

        # Check: Username length
        elif len(username) < 5:
            flash("Username too short (5 characters at minimum).")
            return redirect("/sign_up")

        # Check: Confirm password
        elif password1 != password2:
            flash("Incorrect password.")
            return redirect("/sign_up")

        # Check: Password length
        elif len(password1) < 5:
            flash("Password must be at least 5 characters long.")
            return redirect("/sign_up")

        # Check: DisplayName availability
        if artist:
            flash("Display-name taken.")
            return redirect("/sign_up")

        # Add User to databases
        else:
            new_user = Users(username=username, password=generate_password_hash(password1, method="sha512"))
            db.session.add(new_user)
            user = Users.query.filter_by(username=username).first()
            new_artist = Artists(display_name=display_name, user_id=user.id, note="", 
                                 twitter="", facebook="", youtube="", instagram="", email="")
            db.session.add(new_artist)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account registered.")
            return redirect("/overview")

    # method = GET: Open sign_up form OR redirect if logged in
    else:
        # User: logged in
        if current_user.is_authenticated:
            return redirect("/overview")
        
        # User: NOT logged in
        else:    
            return render_template("authentication/sign_up.html", user=current_user)