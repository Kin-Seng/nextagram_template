from models.base_model import BaseModel
import peewee as pw
from .user import User

class Follower(BaseModel):
    target_user = pw.ForeignKeyField(User)
    follower    = pw.ForeignKeyField(User)
    approve_sts = pw.BooleanField(default=False)



    
