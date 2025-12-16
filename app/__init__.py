from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

migrate = Migrate()

def criar_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "chave-secreta"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///banco.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .views import views_bp
    app.register_blueprint(views_bp)

    with app.app_context():
        from . import models   
        db.create_all()

    return app
