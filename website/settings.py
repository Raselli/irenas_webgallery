import os
from . import db, AVATAR_MAX_SIZE, AVATAR_FOLDER
from .database import Artists
from .entries import allowed_file
from flask import Blueprint, render_template, request, flash, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image


settings = Blueprint("settings", __name__)


# User-Settings: change password, displayname, description artist
@settings.route("/settings", methods=["GET", "POST"])
@login_required
def settings_func():
    
    button_values = ["showprofile", "password", "name", "description", "socialmedia", "email", "avatar"]
    button_texts = ["Show MyProfile", "Change Password", "Display Name", "Description", "Social Media", "Contact (email)", "Avatar"]
    data_buttons = list(zip(button_values, button_texts))

    # Method = POST:
    if request.method == "POST":
        artist = Artists.query.filter(Artists.user_id == current_user.id).first()        
        
        # load change-section
        if request.form.get("change"):
            form = request.form.get("change")
            socialmedias = ['twitter', 'facebook', 'youtube', 'instagram']
            return render_template(f"settings/change_{form}.html", artist=artist, socialmedias=socialmedias, data_buttons=data_buttons)
        
        # get & execute 'change_foo(artist)'
        elif request.form.get("submit"):
            submitted = request.form.get("submit")
            
            # find match for submitted:
            try:
                {
                    "avatar": change_avatar,
                    "description": change_description,
                    "email": change_email,
                    "name": change_name,
                    "password": change_password,
                    "socialmedia": change_socialmedia
                }.get(submitted)(artist)
                return redirect("/settings")
            except:
                abort(500)
        else:
            abort(400)
            
    # Method = GET:
    else:
        return render_template("settings/settings_frame.html", data_buttons=data_buttons)


# Change: Avatar
def change_avatar(artist):  
    file = request.files["file"]

    # Check if filename taken
    if Artists.query.filter((Artists.filename == file.filename)).first():
        flash("File (filename) already exists.")

    # Check for allowed data types (image):
    if file and allowed_file(file.filename):
        artist = Artists.query.filter(Artists.user_id == current_user.id).first()

        # delete existing avatar
        if artist.filename and artist.filename != None:	
            path_old = os.path.join((os.path.dirname(__file__) + AVATAR_FOLDER), artist.filename)               
            os.remove(path_old)	
            artist.filename = None

        # Copy file
        filename = secure_filename(file.filename)
        path = os.path.join((os.path.dirname(__file__) + AVATAR_FOLDER), filename)
        try:
            file.save(path)
        except:
            abort(507)
            
        # Edit file
        image = Image.open(path)                
        width_img, height_img = image.size

        # crop image: portrait (focus on face / top)
        if (height_img > width_img):
            image = image.crop((0, 0, width_img, width_img))

        # crop image: center
        if (height_img < width_img): 			
            rest = (width_img - height_img) / 2		
            image = image.crop((rest, 0, (height_img + rest), height_img))

        # save edited file
        image.thumbnail(AVATAR_MAX_SIZE)
        image.save(path)      
        artist.filename = filename
        db.session.commit()
        flash("Avatar saved.")
    
    # Error: Wrong data type	
    else:
        flash("Allowed file types are: png, jpg, jpeg.")


# Change: artist description
def change_description(artist):  
    artist.note = request.form.get("note")
    db.session.commit()
    flash("Artist-description edited.")


# Change: email
def change_email(artist):       
    artist.email = request.form.get("email")
    db.session.commit()
    flash("E-mail changed.")


# Change: display name
def change_name(artist):  
    name = request.form.get("name").strip()
    name_taken = Artists.query.filter((Artists.display_name == name)).first()
    current_name = Artists.query.filter(Artists.user_id == current_user.id).first()
    
    # Success: Display Name changed
    if ((name.isspace() != True) and name != "None" and name != "") and (name_taken == None or name_taken == current_name):
        artist.display_name = name
        db.session.commit()
        flash("Display name changed!")
                         
    else:
        flash("Invalid display name.")


# Change Password
def change_password(artist):
    password_old = request.form.get("password0")
    password_new1 = request.form.get("password1")
    password_new2 = request.form.get("password2")
    
    # Check: empty form
    if password_old == "" or password_new1 == "" or password_new2 == "":
        flash("Must fill out passwords.")        

    # Check: valid password
    elif check_password_hash(current_user.password, password_old):

        # Check: confirm password match
        if password_new1 != password_new2:
            flash("New password: No match.")

        # Check: no only-space passwords
        elif password_new1.isspace():
            flash("Invalid password.")

        # Check: password too short
        elif len(password_new1) < 5:
            flash("Password must be at least 5 characters long.")

        # Change: password
        else:
            current_user.password = generate_password_hash(password_new1, method="sha512")
            db.session.commit()
            flash("Password changed.")

    # Error: Wrong Password
    else:
        flash("Invalid password.")


# Change: social media
def change_socialmedia(artist):
    artist.twitter = request.form.get("twitter")
    artist.facebook = request.form.get("facebook")
    artist.youtube = request.form.get("youtube")
    artist.instagram = request.form.get("instagram")
    db.session.commit()
    flash("Social media links edited.")