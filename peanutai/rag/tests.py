from bson import ObjectId
import django
import django.conf
from django.test import TestCase
from langchain_openai import AzureChatOpenAI

from rag.utils import GptClient, MongoClient, embed_content
from rag.models import DocSlice256


# Create your tests here.

class RAGTestCase(TestCase):
     def test_mongodb(self):
         doc = MongoClient().get_content_by__id(_id='67309cd339b780cc48f6beab')
         print(doc)
        #  d = DocSlice256.objects.get(_id=ObjectId('67309cd339b780cc48f6beab'))
        #  print(d)
         ...
         
     def test_tongyi(self):
        #  print(embed_content('盗图和信用炒作'))
        ...
     def test_gpt(self):
         ...
        #   print(django.conf.settings.gpt_client)
        #   gpt_client = AzureChatOpenAI(deployment_name="gpt-4o-p", openai_api_version="2024-02-15-preview",azure_endpoint="https://peanut-gpt4o.openai.azure.com/")
        #   print(GptClient().get_client().invoke("讲个笑话"))