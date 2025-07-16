import logging
from flask import Flask
from config import Config
from extensions import ma, bcrypt
from database import init_db
from routers.user_router import user
from routers.todo_router import todo

from dotenv import load_dotenv
load_dotenv()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )

    ma.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(todo, url_prefix='/todo')

    init_db(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
