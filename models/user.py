from models.base_model import BaseModel
import peewee as pw
import hashlib

class User(BaseModel):
    email = pw.CharField(unique=True)
    password  = pw.CharField()
    username = pw.CharField(unique=True)

    def validate(self):
        duplicate_new_user = User.get_or_none(User.username == self.username or User.password==self.password or User.email==self.email)
        
        if duplicate_new_user:
            self.errors.append('Username, password and email is not unique!')


    
