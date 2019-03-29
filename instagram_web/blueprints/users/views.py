from flask import Blueprint, render_template, request,redirect,flash,url_for
from werkzeug.security import generate_password_hash
from models.user import User
# import hashlib

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')
    
#sign up display
@users_blueprint.route('/sign_up', methods=['GET'])
def sign_up():
    return render_template('users/sign_up.html')

#sign up add
@users_blueprint.route('/sign_up/new', methods=['POST'])
def sign_up_new():
    username = request.form['username']
    
    password = request.form['pwd']
    # password = hashlib.md5(password.encode())
    # password = password.hexdigest()
    
    email = request.form['email']

    if len(username) != 0 and len(password) != 0 and (len(email) != 0):
        hashed_pwd = generate_password_hash(password)

        u = User(username=username,password=hashed_pwd,email=email)
        if u.save():
            flash(username + ' Creation Successful!')
            return redirect('/new')
        else:
            return render_template('users/sign_up.html', name=username, errors=u.errors)   

    

@users_blueprint.route('/new/<id>', methods=['POST'])
def create(id):
    pass

@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    pass


@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"


@users_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    pass


@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass
