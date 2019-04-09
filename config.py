import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or os.urandom(32)
    GOOGLE_CLIENT_ID = True 
    GOOGLE_CLIENT_SECRET = True   


class ProductionConfig(Config):
    DEBUG = False
    ASSETS_DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
    ASSETS_DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    ASSETS_DEBUG = False

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    ASSETS_DEBUG = True

# S3 
S3_BUCKET                 = os.environ.get("S3_BUCKET_NAME")
S3_KEY                    = os.environ.get("S3_ACCESS_KEY")
S3_SECRET                 = os.environ.get("S3_SECRET_ACCESS_KEY")
S3_LOCATION               = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

SECRET_KEY                = os.urandom(32)
DEBUG                     = True
PORT                      = 5000

#BrainTree (Payment Gateway)
BT_MERCHANT_ID            = os.environ.get("BT_MERCHANT_ID")
BT_PUBLIC_KEY             = os.environ.get("BT_PUBLIC_KEY")
BT_PRIVATE_KEY            = os.environ.get("BT_PRIVATE_KEY")

#OAuth 2.0 : Google API Keys
GOOGLE_CLIENT_ID = '712067619954-j5uentdlsdoemrsj64qcfv6at7p447uf.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'e3Ae47xeF_GNldG0aHwLZ_is'