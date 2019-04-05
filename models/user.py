from models.base_model import BaseModel
import peewee as pw
import hashlib
from flask_login import UserMixin

class User(BaseModel,UserMixin):
    email = pw.CharField(unique=True)
    password  = pw.CharField()
    username = pw.CharField(unique=True)
    profile_pic = pw.CharField(unique=True,null=True)
    private = pw.BooleanField(default=False)

    def get_user_id(self):
        return self.id

    def validate(self):

        duplicate_new_user = User.get_or_none(User.username == self.username or User.password==self.password or User.email==self.email)
        
        if duplicate_new_user:
            self.errors.append('Username, password and email is not unique!')
