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
    text = None #title 或者 提纲
    text_list = None # 提纲下每个小点的文本，如果是text是title，text_list与text一样
    audio_list = None # 提纲下每个小点的语音，
    status = None
    message = ""
    def __init__(self, type, text=None):
        self.id = uuid.uuid4()
        self.type = type
        self.text = text
        self.text_list = []
        self.audio_list = []
        self.status = TrainStatus.not_start

    def get_text(self):
        return dict(text = self.text,text_list=self.text_list, status = self.status.value, message=self.message)

    def get_audio_list(self):
        return dict( audio_list = self.audio_list, status = self.status.value, message=self.message)

    def get_all_datas(self):
        return dict(text = self.text, text_list=self.text_list,audio_list = self.audio_list, status = self.status.value, message=self.message)

    def load_title(self, title, client: GptClient):
        audio = SpeechSynthesizer.call(
                            model='sambert-zhishuo-v1',
                            text=title,
                            sample_rate=48000,
                            rate=0.9,
                            format='wav'
                        )
        audio_data = audio.get_audio_data()
        self.text_list.append(title)
        self.audio_list.append(base64.b64encode(audio_data).decode('utf-8'))
            
    def load_text(self,outline, client: GptClient):
        try:
            self.status = TrainStatus.training
            _res =  client.invoke_for_outline(outline)
            if len(_res) > 0:
                #原始文本
                self.text = _res 
                #将文本分成开头和具体内容
                text_splits = _res.split('\n\n')
                for split in text_splits:
                    self.text_list.append(split)
                    audio = SpeechSynthesizer.call(
                        model='sambert-zhishuo-v1',
                        text=split,
                        sample_rate=48000,
                        rate=0.9,
                        format='wav'
                    )
                    audio_data = audio.get_audio_data()
                    self.audio_list.append(base64.b64encode(audio_data).decode('utf-8'))
            self.status = TrainStatus.ended
        except Exception as ex:
            self.status = TrainStatus.error
            self.message = f"{ex}"

    #    print(_res)
