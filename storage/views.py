import os
import requests
import threading
import functools
# from django.shortcuts import render
from .helper import replicateBucket, get_address, hinted_handoff
from django.http import HttpResponse, JsonResponse
from cloud.settings import ARCHIVE_DIR
from .models import Bucket, HandoffQueue
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from cloud.settings import AVAILABLE_NODES


# Create your views here.
class ServerStatus(TemplateView):

    def get(self, request):
        return HttpResponse('OK')


@method_decorator(csrf_exempt, name='dispatch')
class CreateBucket(TemplateView):

    def post(self, request):
        name = request.POST.get('name')
        path = os.path.join(ARCHIVE_DIR, name)
        result = ""
        buckets = Bucket.objects.filter(name=name)
        if len(buckets) == 0:
            bucket = Bucket(name=name)
            bucket.save()
            os.makedirs(path)
            result = "Bucket Creation Successful"
        else:
            bucket = Bucket.objects.get(name=name)
            result = "Bucket already exists"
        count = replicateBucket(name)
        data = {'result': result, 'count': count}
        return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class ReplicateBucket(TemplateView):

    def post(self, request):
        name = request.POST.get('name')
        path = os.path.join(ARCHIVE_DIR, name)
        result = ""
        buckets = Bucket.objects.filter(name=name)
        if len(buckets) == 0:
            bucket = Bucket(name=name)
            bucket.save()
            os.makedirs(path)
            result = "Bucket Creation Successful"
        else:
            bucket = Bucket.objects.get(name=name)
            result = "Bucket already exists"
        return HttpResponse(result)


@method_decorator(csrf_exempt, name='dispatch')
class HandleAlive(TemplateView):

    def post(self, request):
        node = request.POST.get('node')
        x = threading.Thread(target=hinted_handoff, args=(node,), daemon=True)
        x.start()
        return HttpResponse('OK')
