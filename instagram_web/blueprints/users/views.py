from flask import Blueprint,Flask, render_template, request,redirect,flash,url_for,session
from werkzeug.security import generate_password_hash,check_password_hash
from models.user import User
from models.images import Images
from app import login_manager,app
from flask_login import login_user, login_required, current_user
from helpers import s3
# import hashlib
import os
from config import S3_LOCATION

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

    upload_file = request.files['profile_pic']

    if len(username) != 0 and len(password) != 0 and (len(email) != 0):
        hashed_pwd = generate_password_hash(password)
        
        upload_file_to_s3(upload_file, os.environ.get('S3_BUCKET_NAME'))

        # upload_file.filename
        u = User(username=username,password=hashed_pwd,email=email,profile_pic=upload_file.filename)
        if u.save():
            flash(username + ' Creation Successful!')
            return render_template('users/user_profile.html')
        else:
            # return redirect('/users/sign_up', name=username, errors=u.errors)
            flash(username + ' Creation Failed!')
            return render_template('users/sign_in.html', name=username, errors=u.errors)


# upload img/files to AWS S3 storage bucket
def upload_file_to_s3(file, bucket_name, acl="public-read"):

    """
    Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
    """

    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return e

    # return "{}{}".format(app.config["S3_LOCATION"], file.filename)
    return "{}{}".format(S3_LOCATION, file.filename)



#user profile display
@users_blueprint.route('/user_profile/<id>', methods=['GET'])
def user_profile(id):
    user = User.get_by_id(id)
    bucket_name =os.environ.get('S3_BUCKET_NAME')    
    return render_template('users/user_profile.html',bucket_name = bucket_name, user=user)
    

#sign in display
@users_blueprint.route('/sign_in', methods=['GET'])
def sign_in():
    return render_template('users/sign_in.html')

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

#user sign in 
@users_blueprint.route('/user_profile', methods=['POST'])
def sign_in_new():
    username = request.form['username']
    password = request.form['pwd']
    
    #search DB
    currentUser = User.get(User.username == username)   

    db_pwd = User.select().where(User.username == username).first().password
    result = check_password_hash(db_pwd, password)

    if currentUser and result :

        # Store user_id in Cookies(In-browser memory)
        # session[:user_id] = User.id
        # request.session['user_id'] = User.id
        # session['user_id']= checkUsername.first().id
        
        # load_user(currentUser)
 
        login_user(currentUser)
        
        flash("Login Successful!")

        # prof_pic = f"http://{os.environ.get('S3_BUCKET_NAME')}.s3.amazonaws.com/{current_user.profile_pic}"
        # return render_template('users/user_profile.html', id = currentUser.id, bucket_name =os.environ.get('S3_BUCKET_NAME') )
        return redirect(url_for("users.user_profile",id=currentUser.id))

    else:
        flash("Wrong Username or Password!")
        return render_template('users/sign_in.html')
 
# display edit screen
@users_blueprint.route('/edit_user/<id>', methods=['GET'])
@login_required
def edit_user(id):
    return render_template('users/edit_user_details.html',id = id)

# update edit screen
@users_blueprint.route('/edit_user/<id>', methods=['POST'])
def update_user(id):

    # file_name = request.file['profile_pic']
    username = request.form['username']
    email = request.form['email']
    old_pwd = request.form['old_pwd']
    new_pwd = request.form['new_pwd']
    new_hash_pwd = generate_password_hash(new_pwd)
    confirm_pwd = request.form['confirm_pwd']

    # current_user.password is in hashed form, while old_pwd is a str
    # check_password_hash doesnt care abt what data type u parsed in
    result = check_password_hash(current_user.password, old_pwd)
    
    if int(id) == current_user.id and result == True and new_pwd == confirm_pwd:
        
        u = User.update(username = username, email=email, password = new_hash_pwd).where(User.id==int(id))
        u.execute()

        flash("Update Successful!")
        
        return render_template('users/edit_user_details.html')
    else:
        flash("Update Failed!")
        return render_template('users/edit_user_details.html')


@users_blueprint.route('/upload_image/<id>', methods=['POST'])
def specific_usr_upload_img(id):
    if current_user.id == int(id):
        #get uploaded img details
        upload_file = request.files['user_upload_img']
        # upload_file = request.files.get('user_upload_img')
        #upload to s3 bucket
        upload_file_to_s3(upload_file, os.environ.get('S3_BUCKET_NAME'))
        #save in DB
        i = Images(user_id=current_user.id,img_name=upload_file.filename)
        if i.save():
            flash('Image Uploaded Successfully!')
            return redirect('/users/user_profile')
        else:
            flash('Upload Image Failed!')
            return render_template('/users/sign_in.html', errors=i.errors)
    else:
        flash('Upload Image Failed aaa!')
        return redirect('/users/sign_in.html')


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
