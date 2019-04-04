from models.base_model import BaseModel
import peewee as pw
from models.user import User

class Images(BaseModel):
    
    img_name = pw.CharField(unique=True)
    user_id = pw.ForeignKeyField(User,backref="images")



    
