import os
# from django.shortcuts import render
from .helper import replicateBucket
from django.http import HttpResponse, JsonResponse
from cloud.settings import ARCHIVE_DIR
from .models import Bucket
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


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
            bucket = Bucket(version=1, name=name)
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
            bucket = Bucket(version=1, name=name)
            bucket.save()
            os.makedirs(path)
            result = "Bucket Creation Successful"
        else:
            bucket = Bucket.objects.get(name=name)
            result = "Bucket already exists"
        return HttpResponse(result)
