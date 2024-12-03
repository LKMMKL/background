import asyncio
import json
import threading

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import dashscope
from dashscope.audio.tts import SpeechSynthesizer

from rag.reponse import response_msg
from rag.utils import GptClient, MmilvusClient, MongoClient

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

class train(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        await self.accept()
       
        
    async def disconnect(self, close_code):
        
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        if(data["type"] == "start_train"):
            title = data['title']
            platorm = data['platform']
            threading.Thread(target=self.sync_retrive, args=(platorm,title)).start()
        # threading.Thread(target=self.sync_retrive, args=("platorm","title")).start()
        
        


    def sync_retrive(self, platform, title):
        try:
            milvus = MmilvusClient()
            monogo = MongoClient()
            gpt = GptClient()
            cols = milvus.query(text=title)     
            if len(cols) == 0:
               raise Exception("content not exist in milvus")
            doc = monogo.get_contents_by_milvus(cols)
            msg = gpt.invoke(title, doc)
            loop.run_until_complete(self._async_send_message(response_msg(code=200, message=msg)))
            # asyncio.run_coroutine_threadsafe(self._async_send_message(dict(msg="nihao")), loop)

        except Exception as ex:
            loop.run_until_complete(self._async_send_message(response_msg(code=500, message=ex)))
    
    async def _async_send_message(self, _msg):
        await self.send_json(_msg)
        print(_msg)
        
class test_train_page1_audio(AsyncWebsocketConsumer):
    async def connect(self):
        # 接受 WebSocket 连接
        await self.accept()

    async def disconnect(self, close_code):
        # 处理断开连接逻辑（如有需要）
        pass

    async def receive(self, text_data):
        try:
            dashscope.api_key = "sk-afb66b016f6b48e4a556ea3bdcf589fa"
            json_data = json.loads(text_data)
            action = json_data.get('action')
            if action == 'startTraining':
                data = json_data.get('data', {})
                provider = data.get('provider')
                title = data.get('title')
                print(f"Received training request for provider: {provider}, title: {title}")
                audiotext = f'你好，我是您的AI培训老师，本节课将由我来教你{title}，课程将由20分钟培训和10分钟答疑组成，下面让我们开始本次的培训课哦。'

                # 发送响应回客户端（如果需要）
                await self.send(text_data=json.dumps({
                    'message': 'Training started successfully'
                }))

                # 调用语音合成 API
                result = SpeechSynthesizer.call(
                    model='sambert-zhishuo-v1',
                    text=audiotext,
                    sample_rate=48000,
                    rate=0.9,
                    format='wav'
                )

                if result.get_audio_data() is not None:
                    # 将音频数据发送回客户端
                    await self.send(bytes_data=result.get_audio_data())
                else:
                    error_message = result.get_response()
                    await self.send(text_data=json.dumps({"error": error_message}))
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Unknown action'
                }))
        except Exception as e:
            await self.send(text_data=json.dumps({"error": str(e)}))
