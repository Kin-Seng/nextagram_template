from models.base_model import BaseModel

from playhouse.hybrid import hybrid_property
import peewee as pw
import hashlib
from flask_login import UserMixin

class User(BaseModel,UserMixin):
    email = pw.CharField(unique=True)
    password  = pw.CharField()
    username = pw.CharField(unique=True)
    profile_pic = pw.CharField(unique=True,null=True)
    private = pw.BooleanField(default=False)

    # def followers(self,selected_user):
        #select all the followers of that specific user

    def get_user_id(self):
        return self.id

    @hybrid_property
    def followers(self):
        from models.follower import Follower
        return User.select().join(Follower, on=(User.id==Follower.follower_id)).where((Follower.target_user_id == self.id))

    @hybrid_property
    def following(self):
        from models.follower import Follower
        return User.select().join(Follower, on=(User.id==Follower.target_user_id)).where((Follower.follower_id == self.id))

    def validate(self):

        duplicate_new_user = User.get_or_none(User.username == self.username or User.password==self.password or User.email==self.email)
        
        if duplicate_new_user:
            self.errors.append('Username, password and email is not unique!')
