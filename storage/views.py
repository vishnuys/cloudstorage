import os
import shutil
import threading
from IPython import embed
from .models import Bucket, File
from cloud.settings import ARCHIVE_DIR
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .helper import replicateBucket, hinted_handoff, replicateDelete, replicateFile, replicateDeleteFile


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
        count = 0
        if len(buckets) == 0:
            os.makedirs(path)
            bucket = Bucket(name=name)
            bucket.save()
            result = "Bucket Creation Successful"
            count += 1
        else:
            bucket = Bucket.objects.get(name=name)
            result = "Bucket already exists"
        count += replicateBucket(name)
        data = {'result': result, 'count': count}
        return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteBucket(TemplateView):

    def post(self, request):
        name = request.POST.get('name')
        path = os.path.join(ARCHIVE_DIR, name)
        result = ""
        buckets = Bucket.objects.filter(name=name)
        count = 0
        if len(buckets) == 0:
            result = "Bucket doesn't exist"
        else:
            shutil.rmtree(path)
            bucket = Bucket.objects.get(name=name)
            bucket.delete()
            result = 'Bucket Deleted Successfully'
            count += 1
        count += replicateDelete(name)
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
            os.makedirs(path)
            bucket = Bucket(name=name)
            bucket.save()
            result = "Bucket Creation Successful"
            return HttpResponse(result)
        return HttpResponseBadRequest('Bucket already exists')


@method_decorator(csrf_exempt, name='dispatch')
class ReplicateDelete(TemplateView):

    def post(self, request):
        name = request.POST.get('name')
        path = os.path.join(ARCHIVE_DIR, name)
        result = ""
        buckets = Bucket.objects.filter(name=name)
        if len(buckets) > 0:
            shutil.rmtree(path)
            bucket = Bucket.objects.get(name=name)
            bucket.delete()
            result = "Bucket delete successful"
            return HttpResponse(result)
        return HttpResponseBadRequest("Bucket doesn't exist")


@method_decorator(csrf_exempt, name='dispatch')
class HandleAlive(TemplateView):

    def post(self, request):
        node = request.POST.get('node')
        stopper = threading.Event()
        x = threading.Thread(target=hinted_handoff, args=(node, stopper), daemon=True)
        x.start()
        return HttpResponse('OK')


@method_decorator(csrf_exempt, name='dispatch')
class CreateFile(TemplateView):

    def post(self, request):
        file = request.FILES['file']
        name = request.POST['name']
        bucket = request.POST['bucket']
        path = os.path.join(ARCHIVE_DIR, bucket, name)
        files = File.objects.filter(name=name)
        buckets = Bucket.objects.filter(name=bucket)
        count = 0
        result = ''
        print(name, files)
        print(bucket, buckets)
        if len(buckets) == 0:
            result = 'No such bucket exists'
        elif len(files) > 0:
            result = 'File already exists. Please use /update/file API to update it.'
        else:
            with open(path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            bucket_model = Bucket.objects.get(name=bucket)
            file_model = File(version=1, name=name, bucket=bucket_model)
            file_model.save()
            result = 'File Creation Successful'
            count += 1
        count += replicateFile(name, bucket, file)
        data = {'result': result, 'count': count}
        return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class ReplicateFile(TemplateView):

    def post(self, request):
        file = request.FILES['file']
        name = request.POST.get('name')
        bucket = request.POST.get('bucket')
        path = os.path.join(ARCHIVE_DIR, bucket, name)
        files = File.objects.filter(name=name)
        buckets = Bucket.objects.filter(name=bucket)
        print(name, files)
        print(bucket, buckets)
        result = ''
        if len(buckets) == 0:
            return HttpResponseBadRequest('No such bucket exists')
        elif len(files) > 0:
            return HttpResponseBadRequest('File already exists. Please use /update/file API to update it.')
        else:
            with open(path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            bucket_model = Bucket.objects.get(name=bucket)
            file_model = File(version=1, name=name, bucket=bucket_model)
            file_model.save()
        return HttpResponse(result)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteFile(TemplateView):

    def post(self, request):
        name = request.POST['name']
        bucket = request.POST['bucket']
        path = os.path.join(ARCHIVE_DIR, bucket, name)
        files = File.objects.filter(name=name)
        buckets = Bucket.objects.filter(name=bucket)
        count = 0
        print(name, files)
        print(bucket, buckets)
        if len(buckets) == 0:
            result = 'No such bucket exists'
        elif len(files) == 0:
            result = 'File doesn\'t exist.'
        else:
            os.remove(path)
            bucket_model = Bucket.objects.get(name=bucket)
            file_model = File.objects.get(name=name, bucket=bucket_model)
            file_model.delete()
            result = 'File Deletion Successful'
            count += 1
        count += replicateDeleteFile(name, bucket)
        data = {'result': result, 'count': count}
        return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class ReplicateDeleteFile(TemplateView):

    def post(self, request):
        name = request.POST.get('name')
        bucket = request.POST.get('bucket')
        path = os.path.join(ARCHIVE_DIR, bucket, name)
        files = File.objects.filter(name=name)
        buckets = Bucket.objects.filter(name=bucket)
        print(name, files)
        print(bucket, buckets)
        if len(buckets) == 0:
            return HttpResponseBadRequest('No such bucket exists')
        elif len(files) == 0:
            return HttpResponseBadRequest('File doesn\'t exist.')
        else:
            os.remove(path)
            bucket_model = Bucket.objects.get(name=bucket)
            file_model = File.objects.get(name=name, bucket=bucket_model)
            file_model.delete()
            result = 'File Deletion Successful'
        return HttpResponse(result)
