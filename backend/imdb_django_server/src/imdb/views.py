from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse

# Create your views here.

class BasicTesting(APIView):
    def get(self,requst):
        return HttpResponse( "Test API")
    
    def post(self,requst):
        _data=requst.data
        return Response(_data)
        