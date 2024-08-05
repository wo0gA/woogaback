from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import *
from .serializers import *
from products.serializers import *
from products.models import *
from django.shortcuts import get_object_or_404
from rest_framework.permissions import *
from django.shortcuts import redirect
from json import JSONDecodeError
from django.http import JsonResponse
import requests
from pathlib import Path
import os, json
from django.core.exceptions import ImproperlyConfigured


class UserDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user = get_object_or_404(User, id=user.id)
        User.update_manner_score(user)
        User.update_level(user)
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        user = request.user
        user = get_object_or_404(User, id=user.id)
        print(request.data)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StoreProductList(APIView): 
    def get(self, request, user_id):
        products = Product.objects.filter(owner_id=user_id)
        serializer = ProductSerializerForRead(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class StoreReviewList(APIView):
    def get(self, request, user_id):
        reviews = Review.objects.filter(product__owner__id=user_id)
        serializer = ReviewSerializerForRead(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR, "secrets.json")

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

#GOOGLE_REDIRECT = get_secret("GOOGLE_REDIRECT")
#GOOGLE_CALLBACK_URI = get_secret("GOOGLE_CALLBACK_URI")
GOOGLE_CLIENT_ID = get_secret("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = get_secret("GOOGLE_SECRET")
GOOGLE_REDIRECT_URI = get_secret("GOOGLE_REDIRECT_URI")

# 구글 로그인을 하면 인증, 인가 승인
# def google_login(request):      
#     scope = "https://www.googleapis.com/auth/userinfo.email " + \
#                 "https://www.googleapis.com/auth/userinfo.profile"
#     return redirect(f"{GOOGLE_REDIRECT}?client_id={GOOGLE_CLIENT_ID}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")

def google_callback(request):
    #프론트에서 인가코드 받아오기
    body = json.loads(request.body.decode('utf-8'))
    code = body['code']
    #code = request.GET.get("code", None)     
    
    if code is None:
        return JsonResponse({'error': 'Authorization code error.'}, status=status.HTTP_400_BAD_REQUEST)

    # 인가코드로 access token 받기
    token_req = requests.post(f"https://oauth2.googleapis.com/token?client_id={GOOGLE_CLIENT_ID}&client_secret={GOOGLE_SECRET}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_REDIRECT_URI}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")

    if error is not None:
        print(error)
        raise JSONDecodeError(error)

    google_access_token = token_req_json.get('access_token')

    # access token으로 구글 정보 가져오기
    user_info = requests.get(f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={google_access_token}")
    res_status = user_info.status_code

    if res_status != 200:
        return JsonResponse({'status': 400,'message': 'Failed to get access token'}, status=status.HTTP_400_BAD_REQUEST)
    
    user_info_json = user_info.json()
    
    extracted_data = User.extract_user_data_by_provider(provider='google', data=user_info_json)

    serializer = OAuthSerializer(data=extracted_data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.validated_data["user"]
        access_token = serializer.validated_data["access_token"]
        refresh_token = serializer.validated_data["refresh_token"]
        first_login = serializer.validated_data["first_login"]
        print(user.profile)
        res = JsonResponse(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "provider": user.provider,
                },
                "message": "login success",
                "token": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                "first_login": first_login,
            },
            status=status.HTTP_200_OK,
        )
        res.set_cookie("access-token", access_token, httponly=True)
        res.set_cookie("refresh-token", refresh_token, httponly=True)
        return res

KAKAO_API = "https://kauth.kakao.com/oauth/authorize?response_type=code"    
KAKAO_TOKEN_API = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_API = "https://kapi.kakao.com/v2/user/me"
KAKAO_CLIENT_ID = get_secret("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI = get_secret("KAKAO_REDIRECT_URI")

# def kakao_login(request):
#     return redirect(f"{KAKAO_API}&client_id={KAKAO_CLIENT_ID}&redirect_uri={KAKAO_REDIRECT_URI}")

def kakao_callback(request):
    #프론트에서 인가코드 받아오기
    body = json.loads(request.body.decode('utf-8'))
    code = body['code']
    
    if code is None:
        return JsonResponse({'error': 'Authorization code error.'}, status=status.HTTP_400_BAD_REQUEST)

    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code": code
    }

    # 인가코드로 access token 받기
    access_token = requests.post(KAKAO_TOKEN_API, data=data).json()['access_token']

    if access_token is None:
        return JsonResponse({'error': 'Access token error.'}, status=status.HTTP_400_BAD_REQUEST)

    # access token으로 사용자 정보 받기
    header = {"Authorization":f"Bearer ${access_token}"}
    user_info_json = requests.get(KAKAO_USER_API, headers=header).json()

    extracted_data = User.extract_user_data_by_provider(provider='kakao', data=user_info_json)

    serializer = OAuthSerializer(data=extracted_data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.validated_data["user"]
        access_token = serializer.validated_data["access_token"]
        refresh_token = serializer.validated_data["refresh_token"]
        first_login = serializer.validated_data["first_login"]
        res = JsonResponse(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "provider": user.provider,
                },
                "message": "login success",
                "token": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                "first_login": first_login,
            },
            status=status.HTTP_200_OK,
        )
        res.set_cookie("access-token", access_token, httponly=True)
        res.set_cookie("refresh-token", refresh_token, httponly=True)
        return res
