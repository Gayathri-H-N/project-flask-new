from extensions import db, migrate
from models import User, ToDo

def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        db.create_all()
    # Ensure sessions are removed after each request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()