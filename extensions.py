from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()
migrate = Migrate()