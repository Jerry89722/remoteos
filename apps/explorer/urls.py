"""remoteOs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/url
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
from django.contrib.auth.decorators import login_required
from django.urls import path
from explorer.views import FileView, InternetView, OnlineMusicView, OnlineFavorView

urlpatterns = [
    path('files/', FileView.as_view(), name='file'),
    path('video/', FileView.as_view(), name='file'),
    path('tv/', FileView.as_view(), name='file'),
    path('online_music/', OnlineMusicView.as_view(), name='online_music'),
    path('internet/', InternetView.as_view(), name='internet'),
    path('favor/', OnlineFavorView.as_view(), name='favor'),
]
