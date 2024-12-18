
from http import HTTPStatus
from bson import ObjectId
import dashscope
from django.conf import settings
from langchain_openai import AzureChatOpenAI
from pymilvus import MilvusClient, Collection
from langchain_core.messages import HumanMessage, SystemMessage
from rag.models import DocSlice256

def test():
    print("test")
    return "test"
class GptClient():

    __client = None

    @classmethod
    def __get_client(cls):
        if cls.__client is None:
            cls.__client = AzureChatOpenAI(deployment_name=settings.DEPLOYE_NAME,openai_api_version=settings.OPENAI_API_VERSION,azure_endpoint=settings.AZURE_ENDPOINT)

        return cls.__client
    def invoke(self, text, knowledge):
        try:
            # messages = [
            #     SystemMessage(content=f"你是花生平台的AI培训老师，你熟悉跨境电商的一切信息,可以根据相关问题准备培训材料，请注意返回一个比较正式的格式。额外的知识库信息:{knowledge}"),
            #     HumanMessage(content=f"请准备有关{text}的知识，并将内容合理划分，且每部分都有一个小标题"),
            #     ]
            self.knowledge = knowledge
            self.title = text
            messages = [
                SystemMessage(content=f"背景信息：{self.knowledge}提示词：你是一个速卖通的AI培训老师，你正在给学生做20分钟的{self.title}培训"),
                HumanMessage(content=f"给这个课程做一个提纲，列三点作为PPT展示文本，你将围绕这三个部分顺序展开培训,注意只能生成返回3点内容，每一点不超过10个字。"),
            ]
            return GptClient.__get_client().invoke(messages).content
        except Exception as ex:
            return ex

    def invoke_for_outline(self, outline):
        try:
            messages = [
                SystemMessage(content=f"背景信息：{self.knowledge}提示词：你是一个速卖通的AI培训老师，你正在给学生做20分钟的{self.title}培训"),
                HumanMessage(content=f"{outline}"),
            ]
            return GptClient.__get_client().invoke(messages).content
        except Exception as ex:
            return ex

class MongoClient():

    def get_by__id(self, _id):
        try:
            doc = DocSlice256.objects.get(_id=ObjectId(_id))
            return doc
        except:
            return None

    def get_content_by__id(self, _id):
        doc = self.get_by__id(_id)
        if doc != None:
            return doc.content
        return ""

    def get_contents_by_milvus(self, _ids):
        # _ids = [obj["slice_id"] for obj in cols]
        doc = ""
        for _id in _ids:
            doc += self.get_content_by__id(_id)
        return doc


class MmilvusClient():
    __client = None

    @classmethod
    def __get_client(cls):
        if cls.__client is None:
            cls.__client = Collection(name='doc_slice256_qwen_v31024')
        return cls.__client

    def query(self, text, limit=3, out_fileds=["slice_id"]):
        res = MmilvusClient.__get_client().search(
            data=[embed_content(text)], anns_field="slice_embedding", limit=3, param={"metric_type": "IP", "top_k": 3}, output_fields=out_fileds)
        if len(res) > 0:
            return res[0].ids
        return []
class TTSClient():
    __client = None

    @classmethod
    def __get_client(cls):
        if cls.__client is None:
            cls.__client = MilvusClient(uri=settings.MILVUS_URL)
        return cls.__client

    def query(self, text, limit=3, out_fileds=["_slice_id"]):
        res = MmilvusClient.__get_client().query(
            collection_name=settings.MILVUS_COLLECTION_NAME,
            embed_content=embed_content(text),
            filter="",
            limit=limit,
            output_fields=out_fileds)
        return res


def embed_content(content):
    resp = dashscope.TextEmbedding.call(
        model=dashscope.TextEmbedding.Models.text_embedding_v3,
        input=content,
        dimension=1024
    )
    if resp.status_code == HTTPStatus.OK:
        slice_embedding = resp["output"]["embeddings"][0]["embedding"]
        return(slice_embedding)
    else:
        print("千问获取slice向量失败")

