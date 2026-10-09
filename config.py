import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-enterprise-ams-2026'
    
    # SQLite database file named database.db in project root
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Megabytes max upload
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads', 'assets')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

