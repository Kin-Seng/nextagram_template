from flask import Blueprint,Flask, render_template, request,redirect,flash,url_for,session
from models.user import User
from models.images import Images
from models.image_donation import Image_donation
from helpers import s3,gateway,message
import os
import peewee as pw
from peewee import prefetch
from flask_login import current_user
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


images_blueprint = Blueprint('images',
                            __name__,
                            template_folder='templates')

#Homepage (Show All pictures of all users)
@images_blueprint.route('/image_gallery', methods=['GET'])
def new():    
    user_with_images = prefetch(User.select(), Images.select())
    return render_template('images/image_galery.html', bucket_name = os.environ.get('S3_BUCKET_NAME'),user_with_images=user_with_images)

#show specific image donation screen 
@images_blueprint.route('/image_donation/<id>', methods=['GET'])
def donation_show(id):
    pic = Images.select().where(Images.user_id==current_user.id, Images.id==int(id)).first()
    #generate token here & pass to html
    client_token = gateway.client_token.generate()
    return render_template('/images/image_donation.html',bucket_name = os.environ.get('S3_BUCKET_NAME'),pic=pic,client_token=client_token)

# process payment for img donation
@images_blueprint.route('/image_donation/<id>', methods=['POST'])
def donation(id):
    # receive nounce from html
    nonce_from_the_client = request.form["payment_nounce"]

    donation_amt = request.form["donation_amt"] 

    # send to braintree server
    result = gateway.transaction.sale({
                "amount": donation_amt,
                "payment_method_nonce": nonce_from_the_client,
                "options": {
                "submit_for_settlement": True
                }
            }) 

    if result.is_success:
        i = Image_donation(img_id=id,doner_id=current_user.id,donation_amt=donation_amt)
        i.save()

        #send email
        message = Mail(
            from_email='from_email@example.com',
            to_emails='kaizerneos@gmail.com',
            subject=f'You have received {donation_amt} for an Image',
            html_content=f'<strong>Your Image (Image_Name) has received {donation_amt} of donation</strong>')
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)


        flash("Donation Successful")
        return redirect(url_for("images.new"))
    else:
        flash("Donation Failed")
        return redirect(url_for("images.donation_show",id=id))
    
#add currency in DB    