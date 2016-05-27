from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from controllers import routes

app = Flask(__name__)
db = SQLAlchemy()

if __name__ == '__main__':
    db.init_app(app)
    app.register_blueprint(routes.app)
    app.run(debug=True)
