import base64
from enum import Enum
import uuid
from django.db import models

from rag.utils import GptClient
from dashscope.audio.tts import SpeechSynthesizer
# Create your models here.
class TrainType(Enum):
    page1 = 1
    page2 = 2
    page3 = 3
    page4 = 4

class TrainStatus(Enum):
    not_start = 0
    training = 1
    ended = 2
    error = 3

class TrainData:
    id = None
    type = None
    text = None
    audio_bytes = None
    status = None
    message = ""
    def __init__(self, type, text=None):
        self.id = uuid.uuid4()
        self.type = type
        self.text = text
        self.status = TrainStatus.not_start

    def get_text(self):
        return dict(text = self.text, status = self.status.value, message=self.message)

    def get_audio_bytes(self):
        return dict(audio_bytes = base64.b64encode(self.audio_bytes).decode('utf-8'), status = self.status.value, message=self.message)

    def get_all_datas(self):
        return dict(text = self.text,audio_bytes = base64.b64encode(self.audio_bytes).decode('utf-8'), status = self.status.value, message=self.message)

    def set_audio_bytes(self, audio_bytes):
        self.audio_bytes = audio_bytes

    def load_text(self,outline, client: GptClient):
        try:
            self.status = TrainStatus.training
            _res =  client.invoke_for_outline(outline)
            if len(_res) > 0:
                self.text = _res
                audio = SpeechSynthesizer.call(
                    model='sambert-zhishuo-v1',
                    text=_res,
                    sample_rate=48000,
                    rate=0.9,
                    format='wav'
                )
            self.audio_bytes = audio.get_audio_data()
            self.status = TrainStatus.ended
        except Exception as ex:
            self.status = TrainStatus.error
            self.message = f"{ex}"

    #    print(_res)
