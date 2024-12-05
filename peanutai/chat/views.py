import asyncio
import json
import threading
from typing import List

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import dashscope
from dashscope.audio.tts import SpeechSynthesizer
from chat.models import TrainData, TrainType
from rag.reponse import response_msg
from rag.utils import GptClient, MmilvusClient, MongoClient
import base64
from django.conf import settings
import uuid
from pymilvus import MilvusClient
from http import HTTPStatus
from rag.models import DocSlice256
from bson import ObjectId
import threading
import time
import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

class train(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.data_list: List[TrainData] = []
        await self.accept()


    async def disconnect(self, close_code):

        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        if(data["action"] == "start_train"):
            title = data['title']
            platorm = data['platform']
            threading.Thread(target=self.sync_retrive, args=(platorm,title)).start()

        # threading.Thread(target=self.sync_retrive, args=("platorm","title")).start()

    def get_page_text(self, action):
        for li in self.data_list:
            if li.type == action:
                return li.text


    def get_page_audio(self, action):
        for li in self.data_list:
            if li.type == action:
                return li.audio_text

    def sync_retrive(self, platform, title):
        try:
            milvus = MmilvusClient()
            monogo = MongoClient()
            gpt = GptClient()
            cols = milvus.query(text=title)
            if len(cols) == 0:
                raise Exception("content not exist in milvus")
            doc = monogo.get_contents_by_milvus(cols)
            #获取提纲
            outline_str = gpt.invoke(title, doc)
            if len(outline_str) < 0:
                raise Exception("outline_str is empty.")
            train_data = TrainData(TrainType.page1, outline_str)
            self.data_list.append(train_data)
            #拆分提纲
            outlines = outline_str.split("\n")
            #按照提纲去提问
            index = 1
            for outline in outlines:
                # 获取gpt文本
                _res = gpt.invoke_for_outline(outline)
                if len(_res) > 0:
                    _train_data = TrainData(index, _res)
                    self.data_list.append(_train_data)
                    index = index + 1
            for li in self.data_list:
                print(f"{li.id} {li.type} {li.text}")
                print(f"==================================")
            # loop.run_until_complete(self._async_send_message(response_msg(code=200, message=msg)))
            # asyncio.run_coroutine_threadsafe(self._async_send_message(dict(msg="nihao")), loop)

        except Exception as ex:
            loop.run_until_complete(self._async_send_message(response_msg(code=500, message=f"{ex}")))

    async def _async_send_message(self, _msg):
        await self.send_json(_msg)
        print(_msg)


async def model_predict(message):
    responses = dashscope.Generation.call(
        model='qwen-plus',
        messages = message,
        result_format='message',  # 设置输出为'message'格式
        stream=True,  # 设置输出方式为流式输出
        # incremental_output=True  # 增量式流式输出
        seed=1234,
        top_p=0.8,
        enable_search=False,
        max_tokens=1500,
        temperature=0.85,
        repetition_penalty=1.0
    )
    return responses



class test_train_page1_audio(AsyncWebsocketConsumer):
    # 用一个字典来存储每个会话的线程
    active_threads = {}

    async def connect(self):
        self.session_id = str(uuid.uuid4())
        await self.accept()
        self.data_list = []

    async def disconnect(self, close_code):
        self.data_list = []
        # 会话断开时，检查并清除该会话的线程
        thread = self.active_threads.get(self.session_id)
        if thread:
            del self.active_threads[self.session_id]
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    async def handle_start_training(self, json_data):
        data = json_data.get('data', {})
        provider = data.get('provider')
        title = data.get('title')
        sessionId = self.session_id
        # 启动新线程来处理 process_rag_predict,将线程添加到 active_threads 字典中，以便在会话结束时能够清除它
        thread = threading.Thread(target=self.process_rag_predict, args=(provider, title, sessionId))
        thread.daemon = True
        thread.start()
        self.active_threads[self.session_id] = thread
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
        sessionId = self.session_id
        type = 'page2Text'
        data = [item for item in self.data_list if item['type'] == type]
        await self.send(text_data=json.dumps(data[0]))

    async def handle_get_page2_audio(self, json_data):
        sessionId = self.session_id
        type = 'page2Audio'
        await asyncio.sleep(1)
        while not any(item['type'] == type for item in self.data_list):
            await asyncio.sleep(1)
        data = [item for item in self.data_list if item['type'] == type]
        await self.send(text_data=json.dumps(data[0]))

    async def handle_get_page3_text(self, json_data):
        sessionId = self.session_id
        type = 'page3Text'
        while not any(item['type'] == type for item in self.data_list):
            await asyncio.sleep(1)
        data = [item for item in self.data_list if item['type'] == type]
        await self.send(text_data=json.dumps(data[0]))


    async def handle_get_page3_audio(self, json_data):
        sessionId = self.session_id
        type = 'page3Audio'
        await asyncio.sleep(1)
        while not any(item['type'] == type for item in self.data_list):
            await asyncio.sleep(1)
        data = [item for item in self.data_list if item['type'] == type]
        await self.send(text_data=json.dumps(data[0]))



    async def handle_get_page4_text(self, json_data):
        sessionId = self.session_id
        type = 'page4Text'
        while not any(item['type'] == type for item in self.data_list):
            await asyncio.sleep(1)
        data = [item for item in self.data_list if item['type'] == type]
        await self.send(text_data=json.dumps(data[0]))

    async def handle_get_page4_audio(self, json_data):
        sessionId = self.session_id
        type = 'page4Audio'
        await asyncio.sleep(1)
        while not any(item['type'] == type for item in self.data_list):
            await asyncio.sleep(1)
        data = [item for item in self.data_list if item['type'] == type]
        await self.send(text_data=json.dumps(data[0]))


    async def handle_get_page5_text(self, json_data):
        sessionId = self.session_id
        type = 'page5Text'
        while not any(item['type'] == type for item in self.data_list):
            await asyncio.sleep(1)
        data = [item for item in self.data_list if item['type'] == type]
        await self.send(text_data=json.dumps(data[0]))


    async def handle_get_page5_audio(self, json_data):
        sessionId = self.session_id
        type = 'page5Audio'
        await asyncio.sleep(1)
        while not any(item['type'] == type for item in self.data_list):
            await asyncio.sleep(1)
        data = [item for item in self.data_list if item['type'] == type]
        await self.send(text_data=json.dumps(data[0]))


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


    @staticmethod
    def qwen_model_predict(message):
        responses = dashscope.Generation.call(
            model='qwen-plus',
            messages=message,
            result_format='message',  # 设置输出为'message'格式
            #stream=True,  # 设置输出方式为流式输出
            seed=1234,
            top_p=0.8,
            enable_search=False,
            max_tokens=1500,
            temperature=0.85,
            repetition_penalty=1.0
        )
        return responses

    @staticmethod
    def qwen_generate_audio(AudioText):
        result = SpeechSynthesizer.call(
            model='sambert-zhishuo-v1',
            text=AudioText,
            sample_rate=48000,
            rate=0.9,
            format='wav'
        )
        return result

    def process_rag_predict(self, provider, title, sessionId):
        # 在这里处理传递的参数

        out_fileds = ["_slice_id"]
        resp = dashscope.TextEmbedding.call(
            model=dashscope.TextEmbedding.Models.text_embedding_v3,
            input=title,
            dimension=1024
        )
        if resp.status_code == HTTPStatus.OK:
            slice_embedding = resp["output"]["embeddings"][0]["embedding"]
            milvusClient = MilvusClient(uri=settings.MILVUS_URL)
            res = milvusClient.query(
                collection_name=settings.MILVUS_COLLECTION_NAME,
                embed_content=slice_embedding,
                filter="",
                limit=10,
                output_fields=out_fileds)

            try:
                # 提取所有 slice_id
                _ids = [obj["slice_id"] for obj in res]
                # 查询并拼接内容
                background = []
                for _id in _ids:
                    doc = DocSlice256.objects.get(_id=ObjectId(_id))
                    if doc:
                        background.append(doc.content)
                backgrounds = "".join(background)
                print(len(backgrounds))

                # 模型开始推理
                # Page2
                message = [{"role":"system","content": f"提示词：你是一个速卖通的AI培训老师，你正在给学生做20分钟的{title}培训计划,背景信息：{backgrounds}"}]
                message.append({'role': 'user', 'content': f"给这个课程做一个提纲，列三点作为PPT展示文本，你将围绕这三个部分顺序展开培训,注意只能生成返回3点内容，每一点不超过10个字。"})
                response = self.qwen_model_predict(message)
                if response["status_code"] == HTTPStatus.OK:
                    #print("res", response)
                    page2Text = {
                        'type': 'page2Text',
                        "code": int(response["status_code"]),
                        "message": response["output"]["choices"][0]["message"].get("content", "")
                    }
                    print("predictPage2Text", page2Text)
                    self.data_list.append(page2Text)
                    #生成语音文本
                    message = [{"role":"system","content": f"提示词：你是一个速卖通的AI培训老师，你正在给学生做20分钟的{title}培训计划,背景信息：{backgrounds}"}]
                    message.append({'role': 'user', 'content': f"{page2Text}是课程中的内容提纲，请按照提纲，用演讲的口吻描述即将要讲的课程内容。注意不需要向别人问好,注意50-100字"})
                    response = self.qwen_model_predict(message)
                    if response["status_code"] == HTTPStatus.OK:
                        predictPage2AudioText =  response["output"]["choices"][0]["message"].get("content", "")
                        print("predictPage2AudioText",predictPage2AudioText)
                        #生成语音
                        result = self.qwen_generate_audio(predictPage2AudioText)
                        if result.get_audio_data() is not None:
                            audio_data = result.get_audio_data()
                            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                            page2Audio={'type': 'page2Audio',
                                        'audioData': audio_base64
                                        }
                            self.data_list.append(page2Audio)
                    else:
                        print("predictPage2AudioText请求失败")
                else:
                    print("predictPage2Text请求失败")


                # Page3
                message = [{"role":"system","content": f"提示词：你是一个速卖通的AI培训老师，你正在给学生做20分钟的{title}培训计划,背景信息：{backgrounds}"}]
                message.append({'role': 'user', 'content': f"给这个课程大纲{page2Text['message']}的‘第一点主题’提炼出6点培训方面,每一点内容可以展开描述不超过10个字,参照示例：违规获取评价：刷单或虚假评价行为。注意不要出现非分点的其他文字或总结"})
                response = self.qwen_model_predict(message)
                if response["status_code"] == HTTPStatus.OK:
                    page3Text = {
                        'type': 'page3Text',
                        "code": int(response["status_code"]),
                        "message": response["output"]["choices"][0]["message"].get("content", "")
                    }
                    print("predictPage3Text", page3Text)
                    self.data_list.append(page3Text)
                    #生成语音文本
                    message = [{"role":"system","content": f"提示词：你是一个速卖通的AI培训老师，你正在给学生做20分钟的{title}培训计划,背景信息：{backgrounds}"}]
                    message.append({'role': 'user', 'content': f"{page3Text['message']}是课程划分的的层面，用演讲的口吻展开讨论课程内容。注意不需要向别人问好,不用分点,注意要在200-400字"})
                    response = self.qwen_model_predict(message)
                    if response["status_code"] == HTTPStatus.OK:
                        predictPage3AudioText =  response["output"]["choices"][0]["message"].get("content", "")
                        print("predictPage3AudioText",predictPage3AudioText)
                        #生成语音
                        result = self.qwen_generate_audio(predictPage3AudioText)
                        if result.get_audio_data() is not None:
                            audio_data = result.get_audio_data()
                            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                            page3Audio={'type': 'page3Audio',
                                        'audioData': audio_base64
                                        }
                            self.data_list.append(page3Audio)
                    else:
                        print("predictPage3AudioText请求失败")
                else:
                    print("predictPage3Text请求失败")


                # Page4
                message = [{"role":"system","content": f"提示词：你是一个速卖通的AI培训老师，你正在给学生做20分钟的{title}培训计划,背景信息：{backgrounds}"}]
                message.append({'role': 'user', 'content': f"给这个课程大纲{page2Text['message']}的‘第2点主题’提炼出6点培训方面,每一点内容可以展开描述不超过10个字,参照示例：违规获取评价：刷单或虚假评价行为。注意不要出现非分点的其他文字或总结"})
                response = self.qwen_model_predict(message)
                if response["status_code"] == HTTPStatus.OK:
                    page4Text = {
                        'type': 'page4Text',
                        "code": int(response["status_code"]),
                        "message": response["output"]["choices"][0]["message"].get("content", "")
                    }
                    print("predictPage4Text", page4Text)
                    self.data_list.append(page4Text)
                    #生成语音文本
                    message = [{"role":"system","content": f"提示词：你是一个速卖通的AI培训老师，你正在给学生做20分钟的{title}培训计划,背景信息：{backgrounds}"}]
                    message.append({'role': 'user', 'content': f"{page4Text['message']}是课程划分的的层面，用演讲的口吻展开讨论课程内容。注意不需要向别人问好,不用分点,注意要在200-400字"})
                    response = self.qwen_model_predict(message)
                    if response["status_code"] == HTTPStatus.OK:
                        predictPage4AudioText =  response["output"]["choices"][0]["message"].get("content", "")
                        print("predictPage4AudioText",predictPage4AudioText)
                        #生成语音
                        result = self.qwen_generate_audio(predictPage4AudioText)
                        if result.get_audio_data() is not None:
                            audio_data = result.get_audio_data()
                            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                            page4Audio={'type': 'page4Audio',
                                        'audioData': audio_base64
                                        }
                            self.data_list.append(page4Audio)
                    else:
                        print("predictPage3AudioText请求失败")
                else:
                    print("predictPage3Text请求失败")


                # Page5
                message = [{"role":"system","content": f"提示词：你是一个速卖通的AI培训老师，你正在给学生做20分钟的{title}培训计划,背景信息：{backgrounds}"}]
                message.append({'role': 'user', 'content': f"给这个课程大纲{page2Text['message']}的‘第3点主题’提炼出6点培训方面,每一点内容可以展开描述不超过10个字,参照示例：违规获取评价：刷单或虚假评价行为。。注意不要出现非分点的其他文字或总结"})
                response = self.qwen_model_predict(message)
                if response["status_code"] == HTTPStatus.OK:
                    page5Text = {
                        'type': 'page5Text',
                        "code": int(response["status_code"]),
                        "message": response["output"]["choices"][0]["message"].get("content", "")
                    }
                    print("predictPage4Text", page5Text)
                    self.data_list.append(page5Text)
                    #生成语音文本
                    message = [{"role":"system","content": f"提示词：你是一个速卖通的AI培训老师，你正在给学生做20分钟的{title}培训计划,背景信息：{backgrounds}"}]
                    message.append({'role': 'user', 'content': f"{page5Text['message']}是课程划分的的层面，用演讲的口吻展开讨论课程内容。注意不需要向别人问好,不用分点,注意要在200-400字"})
                    response = self.qwen_model_predict(message)
                    if response["status_code"] == HTTPStatus.OK:
                        predictPage5AudioText =  response["output"]["choices"][0]["message"].get("content", "")
                        print("predictPage5AudioText",predictPage5AudioText)
                        #生成语音
                        result = self.qwen_generate_audio(predictPage5AudioText)
                        if result.get_audio_data() is not None:
                            audio_data = result.get_audio_data()
                            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                            page5Audio={'type': 'page5Audio',
                                        'audioData': audio_base64
                                        }
                            self.data_list.append(page5Audio)
                    else:
                        print("predictPage3AudioText请求失败")
                else:
                    print("predictPage3Text请求失败")


            except Exception as e:
                print(f"获取内容失败: {e}")
        else:
            print("千问获取slice向量失败")
