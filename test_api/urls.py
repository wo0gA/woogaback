from django.urls import path
from test_api.views import hello_world

urlpatterns = [
    path('', hello_world, name='hello_world')
]