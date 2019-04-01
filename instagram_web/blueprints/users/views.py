from flask import Blueprint,Flask, render_template, request,redirect,flash,url_for,session
from werkzeug.security import generate_password_hash,check_password_hash
from models.user import User
from app import login_manager
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
            return redirect('/users/sign_in')
        else:
            # return redirect('/users/sign_up', name=username, errors=u.errors)
            flash(username + ' Creation Failed!')
            return render_template('users/sign_in.html', name=username, errors=u.errors)


#sign in display
@users_blueprint.route('/sign_in', methods=['GET'])
def sign_in():
    return render_template('users/sign_in.html')

@login_manager.user_loader
def load_user(user_id):
    return User.get(User.id == user_id)

#sign in function
@users_blueprint.route('/sign_in/new', methods=['POST'])
def sign_in_new():
    username = request.form['username']
    password = request.form['pwd']
    
    #search DB
    currentUser = User.select().where(User.username == username)    

    db_pwd = User.select().where(User.username == username).first().password
    result = check_password_hash(db_pwd, password)

    # self.load_user(checkUsername.id)

    if currentUser.count() == 1 and result :    

        # Store user_id in Cookies(In-browser memory)
        # session[:user_id] = User.id
        # request.session['user_id'] = User.id
        # session['user_id']= checkUsername.first().id

        load_user(currentUser)
        # login_user(currentUser)

        flash("Login Successful!")
        return redirect('/users/sign_up')
        
    else:
        flash("Wrong Username or Password!")
        return render_template('users/sign_in.html')
    

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
