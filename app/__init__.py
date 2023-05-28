from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_cors import CORS
from .extensions import db

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:s9927714i@localhost/mydatabase'

    with app.app_context():
        # Allow app to interact with demo frontend
        frontend_host = os.getenv("SGID_FRONTEND_HOST") or "http://localhost:5173"  
        # Initialize CORS within the application context
        CORS(app, origins=[frontend_host], supports_credentials=True)
    
    db.init_app(app)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    from app.models import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app