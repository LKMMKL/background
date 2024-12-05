from enum import Enum
import uuid
from django.db import models

# Create your models here.
class TrainType(Enum):
    page1 = 1
    page2 = 2
    page3 = 3
    page4 = 4

class TrainData:
    id = None
    type = None
    text = None
    audio_text = None

    def __init__(self, type, text):
        self.id = uuid.uuid4()
        self.type = type
        self.text = text

    def set_audio_text(self, audio_text):
        self.audio_text = audio_text

