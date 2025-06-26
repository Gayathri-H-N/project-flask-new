from extensions import db, migrate
from models import User, ToDo

def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        db.create_all()