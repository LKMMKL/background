from functools import wraps
from json import JSONDecoder
import json
from django.http import JsonResponse
from django.shortcuts import render

from rag.utils import GptClient, MmilvusClient, MongoClient
from rag.reponse import response_msg

# Create your views here.
def post_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.method == 'POST':
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse(response_msg(code=404, message="path not exist"))
    return _wrapped_view

@post_required
def get_first_page(request):
    data = json.loads(request.body)
    try:
        if data:
            platform = data['platform']
            title = data['title']
            if not platform or not title:
                raise Exception("params invalid")
            #milvus
            milvus = MmilvusClient()
            monogo = MongoClient()
            gpt = GptClient()
            cols = milvus.query(text=title)     
            if len(cols) == 0:
                raise Exception("content not exist in milvus")
            doc = monogo.get_contents_by_milvus(cols)
            msg = gpt.invoke(title, doc)
            return JsonResponse(response_msg(code=200, message=msg))
    except Exception as ex:
        return JsonResponse(response_msg(code=500, message=ex))
    