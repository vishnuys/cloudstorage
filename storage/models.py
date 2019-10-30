from django.db import models


# Create your models here.
class File(models.Model):
    version = models.IntegerField()
    name = models.CharField(max_length=200, unique=True)
    bucket = models.ForeignKey('Bucket', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class Bucket(models.Model):
    name = models.CharField(max_length=200, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class HandoffQueue(models.Model):
    node = models.CharField(max_length=100)
    function = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    bucket = models.CharField(max_length=200, null=True)
    path = models.CharField(max_length=400, null=True)
