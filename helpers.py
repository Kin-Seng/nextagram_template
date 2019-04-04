# AWS S3 bucket
import boto3, botocore
from config import S3_KEY, S3_SECRET, S3_BUCKET,BT_MERCHANT_ID,BT_PUBLIC_KEY,BT_PRIVATE_KEY

s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET
)


# Braintree - payment gateway
import braintree

#put 3 keys in .env file
gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=BT_MERCHANT_ID,
        public_key=BT_PUBLIC_KEY,
        private_key=BT_PRIVATE_KEY
    )
)



import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail(
    from_email='from_email@example.com',
    to_emails='to@example.com',
    subject='Sending with SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)