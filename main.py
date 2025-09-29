from flask import Flask
import os

from dotenv import load_dotenv
from init import db
from controllers import students_bp, teachers_bp, courses_bp, enrolments_bp, cli_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    db.init_app(app)

    app.json.sort_keys = False

    app.register_blueprint(cli_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(enrolments_bp)

    print('Flask server started')
    return app
