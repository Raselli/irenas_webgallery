import os
from .database import Paintings, Users
from . import db, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, THUMBNAIL_FOLDER, THUMBNAIL_MAX_SIZE
from flask import Blueprint, render_template, flash, request, redirect, abort
from flask_login.utils import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image


entries = Blueprint("entries", __name__)


# allowed filetypes
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# overview: manage entries
@entries.route("/overview", methods=["GET", "POST"])  # change to /entries
@login_required
def overview():

    paintings = Paintings.query.filter((Paintings.user_id == current_user.id)).all()

    # Function: Select action
    def manage_entry(action):
        requests = {
            "list": "entries_list.html",
            "new": "new_entry.html",
            "edit": "select_entry.html",
            "delete": "select_entry.html"
        }
        goto = requests.get(action)
        if goto:
            return goto, action
        else:
            abort(400)

    # Method = Post:
    if request.method == "POST":

        # Overview: Select action (list, new, edit, delete)
        if request.form.get("overview"):
            action = request.form.get("overview")
            requests = manage_entry(action)[0]
            return render_template(f"manage_entries/{requests}", paintings=paintings, action=action)

        # Edit: select entry (dropdown)
        elif request.form.get("edit"):
            action = "edit"
            entry = Paintings.query.filter_by(title=request.form.get("edit")).first()
            return render_template("manage_entries/edit_entry.html", paintings=paintings, entry=entry, action=action)

        # Delete: select entry (dropdown)
        elif request.form.get("delete"):
            action = "delete"
            entry = Paintings.query.filter_by(title=request.form.get("delete")).first()
            return render_template("manage_entries/delete_entry.html", paintings=paintings, entry=entry, action=action)

        else:
            abort(400)

    # Method = Get:
    else:
        return render_template("manage_entries/overview.html", entries=paintings)


#  New Entry: Add data to db & add file(img) to "/static/uploads/"
@entries.route("/new", methods=["POST"])
@login_required
def new_entry():
    user = Users.query.filter_by(username=current_user.username).first()
    user_id = user.id
    title = request.form.get("title").strip()
    alt = request.form.get("alt").strip()
    width = request.form.get("width")
    height = request.form.get("height")
    price = request.form.get("price")
    sold = False
    note = request.form.get("note")

    # check if the post request has the file part
    if "file" not in request.files:
        flash("No file part.")
        return render_template("manage_entries/overview.html")

    file = request.files["file"]

    # Check for empty file:
    if file.filename == "":
        flash("No image selected for uploading.")
        return render_template("manage_entries/overview.html")

    # Check for empty form:
    if title == "" or alt == "" or title == "None" or alt == "None" or title.isspace() == True or alt.isspace() == True or '?' in title:
        flash("Must fill out Alt & Title. Allowed are letters and numbers.")
        return render_template("manage_entries/overview.html")

    # Check if filename taken
    if Paintings.query.filter((Paintings.filename == file.filename)).first():
        flash("File (filename) already exists.")
        return render_template("manage_entries/overview.html")

    # Check if title taken
    if Paintings.query.filter((Paintings.title == title)).first():
        flash("Title already exists.")
        return render_template("manage_entries/overview.html")

    # Check for allowed data types (image):
    if file and allowed_file(file.filename):
        # save image
        filename = secure_filename(file.filename)
        path = os.path.join((os.path.dirname(__file__) + UPLOAD_FOLDER), filename)
        try:
            file.save(path)
        except:
            abort(507)

        # open image for thumbnail creation
        image = Image.open(path)
        width_img, height_img = image.size

        # crop thumbnail img: portrait (focus on face / top)
        if (height_img > width_img):
            image = image.crop((0, 0, width_img, width_img))

        # crop thumbnail img: center
        if (height_img < width_img):
            rest = (width_img - height_img) / 2
            image = image.crop((rest, 0, (height_img + rest), height_img))

        # save thumbnail
        image.thumbnail(THUMBNAIL_MAX_SIZE)
        image.save(os.path.join((os.path.dirname(__file__) + THUMBNAIL_FOLDER), filename))

        # Add entry to "Paintings" in Gallery.database
        new_entry = Paintings(filename=filename, title=title, alt=alt, width=width,
                              height=height, price=price, sold=sold, note=note, user_id=user_id)
        db.session.add(new_entry)
        db.session.commit()

        flash("Painting added to Gallery.")
        return render_template("manage_entries/overview.html")

    # Error: Wrong data type
    else:
        flash("Allowed file types are: png, jpg, jpeg.")
        return render_template("manage_entries/overview.html")


# Edit Entry
@entries.route("/edit", methods=["POST"])
@login_required
def edit_entry():
    entryId = request.form["edit_submit"]
    update = Paintings.query.get(entryId)
    title_edit = request.form.get("title").strip()

    # Verify user
    if update.user_id != current_user.id:
        abort(401)

    # Check for empty and bad input
    if title_edit == "" or title_edit == "None" or title_edit.isspace() == True or '?' in title_edit:
        flash("Must fill out Title. Allowed are letters and numbers.")
        paintings = db.session.query(Paintings).all()
        return render_template("manage_entries/overview.html")

    # Check if title is already taken
    if title_edit != update.title:

        check_title = Paintings.query.filter((Paintings.title == title_edit)).first()

        if check_title != None:
            flash("Title already exists.")
            paintings = db.session.query(Paintings).all()
            return render_template("manage_entries/select_entry.html", paintings=paintings)

        else:
            update.title = title_edit

    # Update Database Entry
    update.alt = request.form.get("alt").strip()
    update.width = request.form.get("width")
    update.height = request.form.get("height")
    update.price = request.form.get("price")
    sold = request.form.get("sold")
    if sold == "sold":
        update.sold = True
    else:
        update.sold = False
    update.note = request.form.get("note")
    db.session.commit()
    flash("Entry edited.")
    return redirect("/overview")


# Delete Entry
@entries.route("/delete", methods=["POST"])
@login_required
def delete_entry():
    entryId = request.form["delete_submit"]
    entry = Paintings.query.get(entryId)
    filename = entry.filename

    # Verify user
    if entry.user_id != current_user.id:
        abort(401)

    # Delete Entry if existing
    if entry:
        flash("Entry deleted.")
        os.remove(os.path.join((os.path.dirname(__file__) + UPLOAD_FOLDER), filename))
        os.remove(os.path.join((os.path.dirname(__file__) + THUMBNAIL_FOLDER), filename))
        db.session.query(Paintings).filter(Paintings.id == entryId).delete()
        db.session.commit()
        return render_template("manage_entries/overview.html")

    else:
        abort(404)