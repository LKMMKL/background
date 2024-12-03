import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from dashscope.audio.tts import SpeechSynthesizer
import dashscope
from dashscope.aigc.generation import AioGeneration

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        app_name = self.scope['url_route']['kwargs']['app_name']
        await self.accept()
        # threading.Thread(target=self.sync_cases, args=()).start()
        
    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(message)


        self.send(text_data=json.dumps({"message": message}))



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
