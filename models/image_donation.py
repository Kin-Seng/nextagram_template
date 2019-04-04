from models.base_model import BaseModel
import peewee as pw
from models.user import User
from models.images import Images

class Image_donation(BaseModel):
    
    img_id          = pw.ForeignKeyField(Images,backref="users")
    doner_id        = pw.ForeignKeyField(User,backref="doner")
    donation_amt    = pw.DecimalField(decimal_places=2)


    
