import werkzeug
from os import path
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# Upload: paths
UPLOAD_FOLDER = '/static/uploads/'
THUMBNAIL_FOLDER = '/static/uploads/thumbnails/'
AVATAR_FOLDER = '/static/uploads/avatars/'

# Upload: file_types
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# Upload: file_sizes
AVATAR_MAX_SIZE = (500, 500)
THUMBNAIL_MAX_SIZE = (300, 300)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Database
db = SQLAlchemy()
DB_NAME = "gallery.db"


# create database "gallery.db"
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database')


# create App
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '998afbc2d4d43321b04faa8c63503da842e27ac4203e25d00c29375b7f761596'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  # sql-alchemy-db located at website-folder
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # image upload: paths, filetypes, size
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER
    app.config['AVATAR_FOLDER'] = AVATAR_FOLDER
    app.config['ALLOWED_EXTENSION'] = ALLOWED_EXTENSIONS
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    
    from .auth import auth
    from .database import Users    
    from .entries import entries
    from .gallery import gallery
    from .settings import settings
    
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(entries, url_prefix='/')
    app.register_blueprint(gallery, url_prefix='/')   
    app.register_blueprint(settings, url_prefix='/')    
     
    # Common error handling 400, 500
    app.register_error_handler(400, bad_request)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, not_found)
    app.register_error_handler(405, not_allowed)   
    app.register_error_handler(413, payload_too_large)          
    app.register_error_handler(500, internal_server_error)
    
    # Custom error handling: 507
    class InsufficientStorage(werkzeug.exceptions.HTTPException):
        code = 507
        description = 'Not enough storage space.'
    app.register_error_handler(InsufficientStorage, insufficient_storage)
        
    create_database(app)

    # Login Manager:
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))

    return app


# error 400
def bad_request(e):
    return render_template('error.html', error=e, nr=400), 400


# error 401
def unauthorized(e):
    return render_template('error.html', error=e, nr=401), 401


# error 403
def forbidden(e):
    return render_template('error.html', error=e, nr=403), 403


# error 404
def not_found(e):
    return render_template('error.html', error=e, nr=404), 404


# error 405
def not_allowed(e):
    return render_template('error.html', error=e, nr=405), 405


# error 413
def payload_too_large(e):
    return render_template('error.html', error=e, nr=413), 413


# error 500
def internal_server_error(e):
    return render_template("error.html", error=e, nr=500), 500


# error 507
def insufficient_storage(e):
    return render_template("error.html", error="507: Insufficient Storage", nr=507), 507