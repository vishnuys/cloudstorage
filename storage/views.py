import os
import shutil
import threading
import mimetypes
from IPython import embed
from .models import Bucket, File
from django.views.generic import TemplateView
from cloud.settings import ARCHIVE_DIR, NODE_NAME
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseNotFound
from .helper import replicateBucket, hinted_handoff, replicateDelete, replicateFile, \
    replicateDeleteFile, replicateUpdateFile


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
        clocks = {}
        print(name, files)
        print(bucket, buckets)
        if len(buckets) == 0:
            result = 'No such bucket exists'
        elif len(files) > 0:
            result = 'File already exists. Please use "/update/filename" API to update it.'
        else:
            with open(path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            bucket_model = Bucket.objects.get(name=bucket)
            file_model = File(version=1, name=name, bucket=bucket_model)
            file_model.save()
            clocks = {NODE_NAME: file_model.version}
            result = 'File Creation Successful'
            count += 1
        rep_count, rep_clocks = replicateFile(name, bucket, file)
        print(rep_count, rep_clocks)
        count += rep_count
        clocks = {**clocks, **rep_clocks}
        data = {'result': result, 'count': count, 'vector_clocks': clocks}
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
        if len(buckets) == 0:
            return HttpResponseBadRequest('No such bucket exists')
        elif len(files) > 0:
            return HttpResponseBadRequest('File already exists. Please use "/update/filename" API to update it.')
        else:
            with open(path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            bucket_model = Bucket.objects.get(name=bucket)
            file_model = File(version=1, name=name, bucket=bucket_model)
            file_model.save()
            result = {'vector': file_model.version, 'status': 'File Creation Successful'}
            return JsonResponse(result)


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
        data = {'result': result, 'count': count, 'vector_clocks': {}}
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


@method_decorator(csrf_exempt, name='dispatch')
class UpdateFile(TemplateView):

    def post(self, request):
        file = request.FILES['file']
        name = request.POST['name']
        bucket = request.POST['bucket']
        path = os.path.join(ARCHIVE_DIR, bucket, name)
        files = File.objects.filter(name=name)
        buckets = Bucket.objects.filter(name=bucket)
        count = 0
        result = ''
        clocks = {}
        print(name, files)
        print(bucket, buckets)
        if len(buckets) == 0:
            result = 'No such bucket exists'
        elif len(files) == 0:
            result = 'File doesn\'t exist.'
        else:
            with open(path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            bucket_model = Bucket.objects.get(name=bucket)
            file_model = File.objects.get(name=name, bucket=bucket_model)
            file_model.version += 1
            file_model.save()
            clocks = {NODE_NAME: file_model.version}
            result = 'File Updation Successful'
            count += 1
        rep_count, rep_clocks = replicateUpdateFile(name, bucket, file)
        print(rep_count, rep_clocks)
        count += rep_count
        clocks = {**clocks, **rep_clocks}
        data = {'result': result, 'count': count, 'vector_clocks': clocks}
        return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class ReplicateUpdateFile(TemplateView):

    def post(self, request):
        file = request.FILES['file']
        name = request.POST.get('name')
        bucket = request.POST.get('bucket')
        vector = int(request.POST.get('vector'))
        timestamp = float(request.POST.get('timestamp'))
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
            bucket_model = Bucket.objects.get(name=bucket)
            file_model = File.objects.get(name=name, bucket=bucket_model)
            if vector > file_model.version:
                with open(path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
                file_model.version += 1
                file_model.save()
                result = 'File Updation Successful'
            elif vector == file_model.version and timestamp > file_model.last_modified.timestamp():
                with open(path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
                file_model.version += 1
                file_model.save()
                result = 'File Updation Successful'
            else:
                result = 'File is version is higher than the recieved file'
            result = {'vector': file_model.version, 'status': result}
            return JsonResponse(result)


@method_decorator(csrf_exempt, name='dispatch')
class FileDownload(TemplateView):

    def get(self, request, bucket, name):
        try:
            bucket_model = Bucket.objects.get(name=bucket)
            file = File.objects.get(name=name, bucket=bucket_model)
            if file:
                print('File exists')
        except ObjectDoesNotExist:
            return HttpResponseNotFound('Invalid File')
        filepath = os.path.join(ARCHIVE_DIR, bucket, name)
        mimetype = mimetypes.MimeTypes().guess_type(filepath)[0]
        response = HttpResponse()
        response['X-Sendfile'] = filepath
        response['Content-Type'] = mimetype
        response['Content-Disposition'] = 'attachment; filename=%s' % name
        return response


@method_decorator(csrf_exempt, name='dispatch')
class GetVector(TemplateView):

    def post(self, request):
        try:
            name = request.POST.get('name')
            bucket = request.POST.get('bucket')
            bucket_model = Bucket.objects.get(name=bucket)
            file = File.objects.get(name=name, bucket=bucket_model)
            result = {'node': NODE_NAME, 'vector': file.version, 'timestamp': file.last_modified.timestamp()}
            return JsonResponse(result)
        except ObjectDoesNotExist:
            return HttpResponseNotFound('Invalid File')


@method_decorator(csrf_exempt, name='dispatch')
class ReadReconciliation(TemplateView):

    def post(self, request):
        try:
            name = request.POST.get('name')
            bucket = request.POST.get('bucket')
            vector = int(request.POST.get('vector'))
            timestamp = float(request.POST.get('timestamp'))
            file = request.FILES['file']
            path = os.path.join(ARCHIVE_DIR, bucket, name)
            bucket_model = Bucket.objects.get(name=bucket)
            file_model = File.objects.get(name=name, bucket=bucket_model)
            if vector > file_model.version:
                with open(path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
                file_model.version = vector
                file_model.save()
                result = 'File Updation Successful'
            elif vector == file_model.version and timestamp > file_model.last_modified.timestamp():
                with open(path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
                file_model.version = vector
                file_model.save()
                result = 'File Updation Successful'
            else:
                result = 'File is version is higher than the recieved file'
            result = {'vector': file_model.version, 'status': result}
            return JsonResponse(result)
        except ObjectDoesNotExist:
            return HttpResponseNotFound('Invalid File')
