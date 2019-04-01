from app import app
from flask import Flask,render_template
from instagram_web.blueprints.users.views import users_blueprint
from flask_assets import Environment, Bundle
from .util.assets import bundles

assets = Environment(app)
assets.register(bundles)

app.register_blueprint(users_blueprint, url_prefix="/users")

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

def create_app(config_filename):
    app = Flask(__name__)
    app.register_error_handler(404, page_not_found)
    return app

@app.route("/")
def home():
    return render_template('home.html')
