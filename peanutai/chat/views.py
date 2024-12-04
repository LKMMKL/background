import asyncio
import json
import threading

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import dashscope
from dashscope.audio.tts import SpeechSynthesizer

from rag.reponse import response_msg
from rag.utils import GptClient, MmilvusClient, MongoClient
import base64
from django.conf import settings
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
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            dashscope.api_key = settings.DASHSCOPE_API_KEY  # 从 Django 设置中获取 API 密钥
            json_data = json.loads(text_data)
            action = json_data.get('action')
            if action == 'startTraining':
                await self.handle_start_training(json_data)
            elif action == 'getPage2Text':
                await self.handle_get_page2_text(json_data)
            elif action == 'getPage2Audio':
                await self.handle_get_page2_audio(json_data)
            elif action == 'getPage3Text':
                await self.handle_get_page3_text(json_data)
            elif action == 'getPage3Audio':
                await self.handle_get_page3_audio(json_data)
            elif action == 'getPage4Text':
                await self.handle_get_page4_text(json_data)
            elif action == 'getPage4Audio':
                await self.handle_get_page4_audio(json_data)
            elif action == 'getPage5Text':
                await self.handle_get_page5_text(json_data)
            elif action == 'getPage5Audio':
                await self.handle_get_page5_audio(json_data)
            elif action == 'getPage6Text':
                await self.handle_get_page6_text(json_data)
            elif action == 'getPage6Audio':
                await self.handle_get_page6_audio(json_data)
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Unknown action'
                }))
        except Exception as e:
            await self.send(text_data=json.dumps({"error": str(e)}))

    async def handle_start_training(self, json_data):
        data = json_data.get('data', {})
        provider = data.get('provider')
        title = data.get('title')
        print(f"Received training request for provider: {provider}, title: {title}")
        audiotext = f'你好，我是您的AI培训老师，本节课将由我来教你{title}，课程将由20分钟培训和10分钟答疑组成，下面让我们开始本次的培训课哦。'

        await self.send(text_data=json.dumps({
            'message': 'Training started successfully'
        }))
        result = SpeechSynthesizer.call(
            model='sambert-zhishuo-v1',
            text=audiotext,
            sample_rate=48000,
            rate=0.9,
            format='wav'
        )
        if result.get_audio_data() is not None:
            audio_data = result.get_audio_data()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            # Send both the audio data and the page identifier
            await self.send(text_data=json.dumps({
                'type': 'page1Audio',
                'audioData': audio_base64
            }))

        else:
            error_message = result.get_response()
            await self.send(text_data=json.dumps({"error": error_message}))

    async def handle_get_page2_text(self, json_data):
        page2_data = json_data.get('data', {})
        print(f"Received request for page 2: {page2_data}")
        await self.send(text_data=json.dumps({
            'type': 'page2Text',
            'code': 200, 'message': '1. 店铺违规行为\n2. 营销基础门槛\n3. 日常数据监控'
        }))

    async def handle_get_page2_audio(self, json_data):
        course_outline = "接下来，我将为您介绍本次课程的大纲。第一，店铺违规行为。第二，营销基础门槛。第三，日常数据监控。让我们开始详细探讨这些主题。"
        result = SpeechSynthesizer.call(
            model='sambert-zhishuo-v1',
            text=course_outline,
            sample_rate=48000,
            rate=0.9,
            format='wav'
        )
        if result.get_audio_data() is not None:
            audio_data = result.get_audio_data()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            # Send both the audio data and the page identifier
            await self.send(text_data=json.dumps({
                'type': 'page2Audio',
                'audioData': audio_base64
            }))
        else:
            error_message = result.get_response()
            await self.send(text_data=json.dumps({"error": error_message}))

    async def handle_get_page3_text(self, json_data):
        page3_data = json_data.get('data', {})
        print(f"Received request for page 3: {page3_data}")
        await self.send(text_data=json.dumps({
            'type': 'page3Text',
            'code': 200,
            'message': "1. 发布禁售商品：销售平台禁止的物品\n2. 使用虚假宣传：夸大产品功能或性能\n3. 冒用品牌商标：未经授权使用商标\n4. 滥发重复产品：重复上传相同商品\n5. 违规获取评价：刷单或虚假评价行为\n6. 描述与实物不符：商品信息与实物差异大"
        }))


    async def handle_get_page3_audio(self, json_data):
        course_outline = "首先是发布禁售商品，平台对某些商品有明确禁止，上传此类产品会面临封禁风险。其次是使用虚假宣传，过度夸大功能不仅损害买家信任，还可能导致投诉。冒用品牌商标是严重侵权行为，轻则下架商品，重则法律追责。滥发重复产品会影响买家的浏览体验，降低店铺权重。违规获取评价，如刷单，不仅得不偿失，还可能导致封店。最后，描述与实物不符，这是造成买家投诉的重要原因，需避免。"
        result = SpeechSynthesizer.call(
            model='sambert-zhishuo-v1',
            text=course_outline,
            sample_rate=48000,
            rate=0.9,
            format='wav'
        )
        if result.get_audio_data() is not None:
            audio_data = result.get_audio_data()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            # Send both the audio data and the page identifier
            await self.send(text_data=json.dumps({
                'type': 'page3Audio',
                'audioData': audio_base64
            }))
        else:
            error_message = result.get_response()
            await self.send(text_data=json.dumps({"error": error_message}))


    async def handle_get_page4_text(self, json_data):
        page4_data = json_data.get('data', {})
        print(f"Received request for page 4: {page4_data}")
        await self.send(text_data=json.dumps({
            'type': 'page4Text',
            "code": 200,
            "message": "1. 提供合法资质：店铺需具备有效营业执照\n2. 确保产品合规：商品符合速卖通销售政策\n3. 完善物流保障：提供准确及时的物流服务\n4. 制定合理价格：避免恶性竞争或定价过高\n5. 提供优质客服：及时响应客户咨询和问题\n6. 保证商品质量：确保产品符合描述和标准"
        }))

    async def handle_get_page4_audio(self, json_data):
        course_outline = "提供合法资质是入驻的基本要求，确保营业执照有效且真实。其次，确保产品合规，商品必须符合平台的政策与规范。完善物流保障也是关键，精准发货和高效物流能提升客户满意度。制定合理价格避免恶性竞争，同时让买家感到物有所值。提供优质客服，快速回应买家的咨询，建立信任感。最后，保证商品质量，严格把控质量，确保产品与描述一致，减少纠纷。合规运营，提升服务，才能实现店铺的长期发展！"
        result = SpeechSynthesizer.call(
            model='sambert-zhishuo-v1',
            text=course_outline,
            sample_rate=48000,
            rate=0.9,
            format='wav'
        )
        if result.get_audio_data() is not None:
            audio_data = result.get_audio_data()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            # Send both the audio data and the page identifier
            await self.send(text_data=json.dumps({
                'type': 'page4Audio',
                'audioData': audio_base64
            }))
        else:
            error_message = result.get_response()
            await self.send(text_data=json.dumps({"error": error_message}))


    async def handle_get_page5_text(self, json_data):
        page5_data = json_data.get('data', {})
        print(f"Received request for page 5: {page5_data}")
        await self.send(text_data=json.dumps({
            'type': 'page5Text',
            "code": 200,
            "message": "1. 流量数据监控：分析店铺每日访客数量\n2. 转化率跟踪：统计访客购买转化情况\n3. 商品销量监控：追踪热销与滞销产品数据\n4. 客户评价分析：收集买家反馈优化服务\n5. 物流时效监控：确保订单按时发货与送达\n6. 竞争对手对比：定期检查市场价格与策略"
        }))


    async def handle_get_page5_audio(self, json_data):
        course_outline = "流量数据监控，要及时了解每日访客量，评估流量来源是否高效。其次是转化率跟踪，分析访客转化为买家的比例，优化页面设计和营销策略。商品销量监控帮助我们判断热销与滞销产品，调整库存结构。客户评价分析能让我们了解买家的真实需求，不断提升服务质量。物流时效监控确保订单及时发货，提高买家的满意度。最后，竞争对手对比，定期关注市场价格与策略，保持竞争力。通过数据驱动，提升运营效率和店铺表现！"
        result = SpeechSynthesizer.call(
            model='sambert-zhishuo-v1',
            text=course_outline,
            sample_rate=48000,
            rate=0.9,
            format='wav'
        )
        if result.get_audio_data() is not None:
            audio_data = result.get_audio_data()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            # Send both the audio data and the page identifier
            await self.send(text_data=json.dumps({
                'type': 'page5Audio',
                'audioData': audio_base64
            }))
        else:
            error_message = result.get_response()
            await self.send(text_data=json.dumps({"error": error_message}))


    async def handle_get_page6_text(self, json_data):
        page6_data = json_data.get('data', {})
        print(f"Received request for page 6: {page6_data}")
        await self.send(text_data=json.dumps({
            'type': 'page6Text',
            "code": 200,
            "message": "答疑"
        }))


    async def handle_get_page6_audio(self, json_data):
        course_outline = "接下来我们将进入课程的10分钟答疑环节，任何有关课程内容请向我提问，非课程相关部分原谅我无法作答哦，如果没有问题也可以随时点击结束本次课程哦"
        result = SpeechSynthesizer.call(
            model='sambert-zhishuo-v1',
            text=course_outline,
            sample_rate=48000,
            rate=0.9,
            format='wav'
        )
        if result.get_audio_data() is not None:
            audio_data = result.get_audio_data()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            # Send both the audio data and the page identifier
            await self.send(text_data=json.dumps({
                'type': 'page6Audio',
                'audioData': audio_base64
            }))
        else:
            error_message = result.get_response()
            await self.send(text_data=json.dumps({"error": error_message}))
