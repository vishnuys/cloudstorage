from django.db import models


# Create your models here.
class File(models.Model):
    version = models.IntegerField()
    filename = models.CharField(max_length=200)
    filepath = models.CharField(max_length=400)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
