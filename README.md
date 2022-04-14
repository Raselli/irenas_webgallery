# Irena's WebGallery
#### Video Demo:  <https://youtu.be/nFt_DnLmOZg>
#### Description:
Irena's WebGallery is a web app allowing registered users to upload their art and to present themselves using a profile.

•	Allows creation of profiles, uploading of pictures with description and more.
•	Pictures are saved inside a folder-system and are referred to a profile inside a database.
•	Submitted as [final project for CS50x](https://youtu.be/nFt_DnLmOZg) in 2021.


## What was used for creating this Web App
The web app was made using CSS, HTML, Python v3.9.9

Python: The following frameworks / libraries / extensions were used:
- Flask
- Jinja
- Werkzeug
- SQLAlchemy
- Pillow

HTML & CSS: Buttons and other tag-modifications are from:
- w3schools
- bootstraps

PURE CSS Gold Text for CSS is made by Addison Legere:
https://addisonlegere.com/

## How the web app works:
### The website is divided into several sections. 
Home, gallery, artists (all), artist-profiles and the uploaded paintings are publicly accessible.
Visitors can register an account and will then gain access to the overview via "manage entries" where they have the possibility to upload and manage their images. Further, users are allowed to modify their profile.

#### Website - Header
Via the header visitors can access home, the gallery and the list of all artists.
Additionally, in the website’s header users have access to “signup” and “login”. When logged in, these will change into "manage entries"-link and "logout" buttons.

#### Manage Entries / overview - Section
Via manage-entries-link (website's header), registered users gain access to the overview section.
Below the website's header the following buttons will appear:

##### My Entries – Section
“My Entries” loads a table containing thumbnails of the user’s uploaded images and all information about the upload stored inside a database.

##### New Entry - Section
This section allows the user to upload an image and store information about the image. Images will be uploaded to ./website/uploads/ and a thumbnail with a smaller resolution (300px*300px) will be created.

##### Edit Entry - Section
This section allows the user to edit information about existing entries

##### Delete Entry - Section
This section allows the user to delete existing entries

##### Settings - Section
This section allows the user to access the user's profile for editing.
The settings-section allows the user to change: username, password, description, social media, email and avatar-picture.
The information will be stored in Gallery.db under Artists. The avatar will be saved with a 500px*500px resolution inside ./website/uploads/avatars/.

## Routing
Managing entries and modifying the profile require to be logged in. Authentication will be checked using the login-decorator from flask_login.
Under SignUp and home, visitors are able to register an account. Accounts are stored inside Gallery.db under Users. Passwords are encrypted using SHA512.

## Sessions
Once logged in, the session will be stored. The sessions are handled via flask_login. As for now, the session will never expire.

## Database - Gallery.db
All information is stored inside Gallery.db. If not already existing, Gallery.db is created on running the app.

Gallery.db is divided into three databases:
- Users, containing: id (key), username and the hashed password
- Paintings, containing: id (key), filename (unique, mandatory), title (unique, mandatory), alt (unique, mandatory), with, height, price, sold, note, timestamp and user-id (foreign-key from Users.).
- Artists, containing: id (key), display_name (unique, mandatory), filename (unique), note, twitter, facebook, youtube, instagram, email and user-id (foreign-key from Users.). 

User and Artist database entries are committed by creating the account. The Painting database entry is created upon submitting a new entry under the "New Entry" section. Artists and Paintings databases are related to Users via the user-id foreign key.

## Uploads
Uploaded images are stored inside the static folder. Avatars and thumbnails are stored in separate folders inside the static folder.
Avatars and thumbnails are edited automatically with intention to get the face on the painting(if there is one) in the middle of the thumbnail or avatar.
The filename is stored under Paintings inside Gallery.db.
The deletion of images inside the static folder is handled simultaneously to the deletion of the file name inside the Paintings database.
The handling of the folders has to occur manually via access to the folders or via the database.

## Code (Structure)
### Python Files
The python code is divided into multiple sections.

#### app.py
Running “app.py” inside the main folder (./irenas_webgallery/) will run the app. 

#### __app__.py
Running the app via app.py runs __app__.py.
- If there is no database on running the app, a new database will be created
- The folder-paths for uploading images, the allowed file-types and the resolution as well as maximum file-size are handled in __app__.py
- All blueprints, the database and errors are registered in __app__.py

#### auth.py
auth.py handles login, logout and sign_up routes. By signing up, the account-information is stored inside Users & Artists in Gallery.db.

#### database.py
Specification for the creation of Gallery.db: Users, Paintings and Artists. Explained in: "Gallery.db - Database" (above).

#### entries.py
Loads "Overview” on the website via overview-route. Also handles the routes for new entry, edit entry and delete entry. Login required.

#### gallery.py
Handles the following routes: Index (Home), gallery, enlarge-image, artists and artist (profile with entries).

#### settings.py
Handles: Show profile, change avatar, description, email, display name, password and social media via the settings_func-route. 

### HTML-Files
The templates folder contains the following sub-folders: 
- Authentication: templates for auth.py
- Manage_entries: templates for entries.py
- Settings: templates for settings.py

## Running the Program
Run "app.py" using Python 3.9.9 64-bit.
As for now, the app won't work with newer versions of Python (Version 3.10).
The following is required for running the app:
- Flask
- Werkzeug
- SQLAlchemy
- Pillow
