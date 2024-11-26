from mongoengine import *

from peanutai.settings import DATABASES

# Create your models here.



class DocSlice256(Document):
    _id = EmailField()
    doc_id = EmailField()
    title = StringField() 
    platform = StringField() 
    create_date = DateTimeField()
    record_date = DateTimeField()
    type = StringField() 
    slice_number = IntField()
    content = StringField() 

