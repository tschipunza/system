from flask import Flask
import pymysql
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

# Upload folder configuration
UPLOAD_FOLDER_FUEL = 'static/uploads/fuel_receipts'
UPLOAD_FOLDER_SERVICE = 'static/uploads/service_invoices'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_FUEL
app.config['UPLOAD_FOLDER_SERVICE'] = UPLOAD_FOLDER_SERVICE
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folders if they don't exist
os.makedirs(UPLOAD_FOLDER_FUEL, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_SERVICE, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# MySQL connection function
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='ts#h3ph3rd',
        database='flask_auth_db',
        cursorclass=pymysql.cursors.DictCursor
    )

# Import routes after app initialization
from routes import *

if __name__ == '__main__':
    app.run(debug=True)
