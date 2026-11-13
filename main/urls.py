from django.urls import path
from main.views import *
from courses.views import *


urlpatterns = [
    path("", index,name='dashboard2'),
]