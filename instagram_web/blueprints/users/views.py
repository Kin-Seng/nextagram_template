from flask import Blueprint,Flask, render_template, request,redirect,flash,url_for,session,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from models.user import User
from models.images import Images
from models.follower import Follower
from app import login_manager,app
from flask_login import login_user, login_required, current_user
from helpers import s3
# import hashlib
import os
from config import S3_LOCATION


from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


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
            return render_template('users/user_profile.html',user=current_user)
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
    #current profile user_id
    user = User.get_by_id(id)
    bucket_name = os.environ.get('S3_BUCKET_NAME')  
    if id != current_user.id:
        follow = Follower.select().where(Follower.target_user==user, Follower.follower_id==current_user.id).first()
        
        # followers
        followers = Follower.select().join(User, on=(Follower.target_user == User.id)).where(Follower.target_user == id).count()

        # following
        following = Follower.select().join(User, on=(Follower.follower_id == User.id)).where(Follower.follower_id == id).count()

        return render_template('users/user_profile.html',bucket_name = bucket_name, user=user, follow = follow, followingNo = following, followersNo = followers)
    else:
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
 
from helpers import oauth

######   Each Service API will have 1 set of 2 functions below  ######
@users_blueprint.route('/login', methods=["GET"])
def login():
    redirect_uri = url_for('users.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@users_blueprint.route('/authorize', methods=["GET"])
def authorize():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()
    email = user_info['email']

    # email = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()['email']

    result = User.select().where(User.email == email).first()
    # you can save the token into database

    if result: 
        # redirect to this user's profile page
        return redirect(url_for("users.user_profile",id=result.id))
        
    else:
        #create a new acc for this user
        
        #sign him in & redirect to his own profile page  
        flash("Email do not exist. Please register yourself in our App using ur email address")
        return redirect(url_for("users.sign_up"))    
    
    

##########################################################################
@users_blueprint.route('/follow/<user_id>')
def follow(user_id):
    
    user_id = int(user_id)
    
    #save in Follower table
    Follower(target_user=user_id,follower_id=current_user.id).save()

    f = Follower.select().where(Follower.target_user==user_id, Follower.follower_id==current_user.id).first()
    
    #send email , rmb to include link with the target user's id
    # message = Mail(
    #     from_email='from_email@example.com',
    #     to_emails='kaizerneos@gmail.com',
    #     subject=f'{current_user.username} requested to follow you!',
    #     html_content=f'<strong>Here are the links to view all your Fan requests <a href="http://localhost:5000/users/fan_request/{user_id}">http://localhost:5000/users/fan_request/{user_id}</a></strong>')
    # try:
    #     sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    #     response = sg.send(message)
    #     print(response.status_code)
    #     print(response.body)
    #     print(response.headers)
    # except Exception as e:
    #     print(e.message)


    
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    return render_template('/users/user_profile.html',bucket_name = bucket_name, user=user_id, follow = f)

@users_blueprint.route('/unfollow/<user_id>')
def unfollow(user_id):

    Follower.delete().where(Follower.target_user==user_id, ).execute()

    pass


# @users_blueprint.route('/privacy')
# def chgPrivacy():




# fan request list display view
@users_blueprint.route('/fan_request/<id>', methods=['GET'])
def fan_request(id):    
    user = User.get_by_id(id)
    fan_request_list = user.followers.where(Follower.approve_sts == False, Follower.target_user == id)

    bucket_name = os.environ.get('S3_BUCKET_NAME')
    return render_template('users/fan_request.html',bucket_name = bucket_name,fan_request_list = fan_request_list)


# accept fan request
@users_blueprint.route('/accept_request/<id>', methods=['GET'])
def accept_request(id):
    
    id=int(id)
    # ar = Follower.select().where(Follower.target_user == id and  Follower.follower_id = cur_user_id)
    user = User.get_by_id(id) 
    fan_list = user.followers.where(Follower.approve_sts == False, Follower.target_user==id)
    
    # update Follower table
    f = Follower.update(approve_sts=True).where(Follower.approve_sts==False, Follower.target_user==id , Follower.follower_id==current_user.id)
    f.execute()
    # breakpoint()

    bucket_name = os.environ.get('S3_BUCKET_NAME')
    return render_template('users/fan_request.html',bucket_name = bucket_name,user=user,fan_request_list=fan_list)


# reject fan request
@users_blueprint.route('/reject_request/<id>', methods=['GET'])
def reject_request(id):
    id=int(id)

    current_user.id = 39

    user = User.get_by_id(id) 
    fan_list = user.followers.where(Follower.approve_sts == False, Follower.target_user==id)

    #delete record in Follower table
    f = Follower.delete().where(Follower.approve_sts==False, Follower.target_user==current_user.id , Follower.follower_id==id)
    f.execute()

    # breakpoint()

    bucket_name = os.environ.get('S3_BUCKET_NAME')
    return render_template('users/fan_request.html',bucket_name = bucket_name, user=user ,fan_request_list=fan_list)


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
