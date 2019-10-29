from django.db import models


# Create your models here.
class File(models.Model):
    version = models.IntegerField()
    name = models.CharField(max_length=200, unique=True)
    bucket = models.ForeignKey('Bucket', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class Bucket(models.Model):
    version = models.IntegerField()
    name = models.CharField(max_length=200, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
