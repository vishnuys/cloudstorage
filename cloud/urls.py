"""new URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from storage import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('status/', views.ServerStatus.as_view()),
    path('createbucket/', views.CreateBucket.as_view()),
    path('replicate/', views.ReplicateBucket.as_view()),
    path('deletebucket/', views.DeleteBucket.as_view()),
    path('replicate_delete/', views.ReplicateDelete.as_view()),
    path('createfile/', views.CreateFile.as_view()),
    path('replicatefile/', views.ReplicateFile.as_view()),
    path('deletefile/', views.DeleteFile.as_view()),
    path('replicatedeletefile/', views.ReplicateDeleteFile.as_view()),
    path('updatefile/', views.UpdateFile.as_view()),
    path('replicateupdatefile/', views.ReplicateUpdateFile.as_view()),
    path('alive/', views.HandleAlive.as_view()),
    path('gossip/', views.HandleGossip.as_view()),
    path('getvector/', views.GetVector.as_view()),
    path('reconciliation/', views.ReadReconciliation.as_view()),
    path('file/<bucket>/<name>', views.FileDownload.as_view()),
]
