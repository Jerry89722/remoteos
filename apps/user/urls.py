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
from django.conf.urls import url
from django.urls import path

from user.views import RegisterView, ActiveView, LoginView, UserInfoView

urlpatterns = [
    url(r'^register$', RegisterView.as_view(), name='register'),
    # path('active/<str:token>', ActiveView.as_view(), name='active'),
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),
    path('login', LoginView.as_view(), name='login'),
    url(r'^$', UserInfoView.as_view(), name='user'),
]
