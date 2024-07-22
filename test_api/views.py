from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
def hello_world(request):
    if request.method == "GET":
        return JsonResponse({
            'status' : 200,
            'data' : "Hello World!!!"
        }, status=200)