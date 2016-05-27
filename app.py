from flask import Flask

from models import db
from controllers import routes

app = Flask(__name__)
app.config.from_object('config')

if __name__ == '__main__':
    db.init_app(app)
    app.register_blueprint(routes.app)
    app.run(debug=True)
