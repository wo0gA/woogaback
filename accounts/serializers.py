from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import RefreshToken
from allauth.socialaccount.models import SocialAccount

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username','email']

class OAuthSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'provider']
    
    def validate(self, data):    
        email = data.get('email', None)
        username = data.get('username', None)
        provider = data.get('provider', None)

        if email is None:
            raise serializers.ValidationError('Email does not exist.')
        
        if username is None:
            username = email.split('@')[0]  
       
        user = User.get_user_by_email(email=email, provider=provider)

        if user is None:
            user = User.objects.create(email=email, username=username, provider=provider)
            user.save()
        
        token = RefreshToken.for_user(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        data = {
            "user": user,
            "refresh_token": refresh_token,
            "access_token": access_token,
        }

        return data